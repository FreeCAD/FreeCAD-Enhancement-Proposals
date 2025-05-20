| FEP-0002           |                                                                   |
| ------------------ | ----------------------------------------------------------------- |
| **Title**          | Asynchronous Document Recompute and Multithreading Infrastructure |
| **Type**           | Core Change                                                       |
| **Status**         | Draft                                                             |
| **Author(s)**      | Joao Matos (tritao)                                               |
| **Version**        | 0.1                                                               |
| **Created**        | 2025-05-20                                                        |
| **Updated**        | 2025-05-20                                                        |
| **Discussion**     | TBD                                                               |
| **Implementation** | TBD                                                               |

A proposal to introduce foundational asynchronous and multithreaded infrastructure in FreeCAD, improving UI responsiveness and paving the way for parallel document recomputation.

## Context

FreeCAD’s code runs mostly entirely on the main thread: Python scripts, Qt event loop (including rendering and event dispatch), and OCCT operations all execute in sequence. When a long-running OCCT computation occurs during Qt’s event loop, it blocks incoming events—pausing UI updates, preventing user interaction, and stalling rendering until the operation completes. Currently, the only way to stop such a blocking computation is to kill the application outright, resulting in potential data loss and non-optimal user experience.

## Motivation

FreeCAD’s current document recompute and signal system operate synchronously, often blocking the UI during heavy OCCT computations.

As models grow in complexity, users experience lags and freezes that impede productivity. By offloading compute-intensive tasks into asynchronous and multithreaded workflows, we can maintain a responsive interface and prepare the codebase for future parallelization of the document DAG.

## Rationale

The core driver of this proposal, has been to run feature transformation commands (e.g., Part and PartDesign operations) in the background, ensuring the UI remains interactive, while making minimal changes to the data model, as well as allowing parallel creation of FreeCAD objects, as long as they don't touch shared state.

## Specification

### Document Recompute Thread

Introduce a dedicated recompute worker thread that will accept and process document recompute requests in FIFO order. Most common recompute requests originate from:

* **Refresh commands**: User-initiated UI actions that trigger a full document recompute.
* **Python document recompute requests**: Scripts invoking `App::Document::recompute()`.
* **Feature transformation commands**: Part and PartDesign operations that modify features and require recompute.
* **Property changes**: When data changes, `onChange` signal triggers recomputation.

The recompute thread will handle:

1. Receiving and queuing requests.
2. Executing recompute logic off the main thread.
3. Handling abort signals to cancel in-progress operations.
4. Posting completion events back to the Qt main loop for UI update.

### Concurrency Constraints

While recompute is running, other code paths in the main thread may post events or callbacks that invoke FreeCAD APIs, including :

* `QTimer`-based callbacks
* `QProcess` and `QThread` signals
* `QNetworkAccessManager` responses
* Python `asyncio` loops integrated with Qt (QtAsyncio)

  QtAsyncio is a module that provides integration between Qt and Python’s [asyncio](https://docs.python.org/3/library/asyncio.html) module. It allows you to run asyncio event loops in a Qt application, and to use Qt APIs from asyncio coroutines.

Allowing such callbacks to run against a document undergoing background recompute risks data races and inconsistent state. To prevent this, the following approaches are considered:

1. **GIL-based blocking**: Hold the Python GIL for the duration of recompute to prevent any Python callbacks from executing. This blocks external Python code from running but may cause temporary UI lockups if code in the main thread attempts to acquire the GIL while the recompute worker thread is processing a request.

    Addons that currently call FreeCAD APIs on event loop hooks will be the main source of such lockups, but worst case scenario they might cause an UI lockup similar to the current status-quo.

2. **Event filtering**: Install a Qt event filter (`qApp->installEventFilter`) that intercepts and queues specific event types during recompute, replaying them afterward. This prevents concurrent execution but adds complexity in managing queued events.

3. **Fine-grained locking**: Release the GIL and allow callbacks to run concurrently, but enforce mutex-based locking around all FreeCAD state accesses (via the recursive shared mutex). This general solution supports parallelism at the cost of broader code changes and potential performance overhead.

   Further consideration about this approach is made below, in the "Shared Recursive Locking for Core Data Model" document section.

#### Signal Emission Threading

FreeCAD’s application and document object signals are emitted in the thread where processing occurs. When invoked from the recompute worker thread, these signals may trigger Qt or Coin operations—which must run on the UI thread to be safe. Two options exist:

* **Worker-thread emission with UI scheduling**: Allow the worker thread to emit signals, but require handlers to detect UI-bound operations and reschedule them via `QMetaObject::invokeMethod` or post events to the main loop.
* **UI-thread signal dispatch**: Queue signal emission events and only emit them from within the Qt main thread, ensuring all handlers run in the correct context (at the cost of potential latency and reduced throughput).

Regarding signals, it remains unclear which approach offers the best trade-off; prototypes have focused on worker-thread emission with UI scheduling, while the UI-thread dispatch model could be safer by default, but also a bit less performant due to potentially less recompute work being done on the worker thread.

### Shared Recursive Locking for Core Data Model

To safely allow concurrent access and avoid data races during background recompute (and other parallel operations), introduce a lightweight, recursive shared reader–writer mutex across key FreeCAD data model classes. This mutex supports multiple concurrent readers (shared locks) or one writer (exclusive lock), and recursion within the same thread for convenience.

* **Design goals**:

  * **Efficiency**: Minimize overhead by keeping locking coarse enough to avoid heavy contention, yet fine-grained enough to allow parallel read-only access.
  * **Simplicity**: Use a single mutex type (`RecursiveSharedMutex`) rather than a proliferation of lock types.
  * **Consistency**: Apply uniformly to core data containers to enforce a clear synchronization model.

* **Initial candidates** (see Appendix A)

Background recompute thread and any other worker threads will acquire the appropriate lock before reading or modifying model state. Main thread operations (e.g., UI commands, Python callbacks) also acquire locks, ensuring mutual exclusion or safe concurrent reading.

However careful consideration needs to be done to make sure we release the Python GIL while waiting for the lock to be available. It would look similar to a spinlock (`try_lock`), where we would wake the thread, and check if its safe to continue (write lock and Python GIL available).

To note this still has the risk of potentially locking the UI thread for the duration of the recompute loop, but it could only happen for a certain subset of addons that hook the Qt event loop and need to read/mutate state during such events.

### Impact on existing subsystems / features

* **Add-ons** relying on synchronous hooks may require adaptation to async callbacks, depending on which async synchronization model is chosen.
* **Performance**: Shared Recursive Locking will introduce some overhead, it's unclear how much)

### Python GIL Considerations

Some heavy operations in FreeCAD (e.g., mesh generation via `meshFromShape`) temporarily release the Python GIL using `PyGILState_Release`/`PyGILState_Ensure`.  While GIL release allows other Python threads to run, it complicates synchronization between Python and C++ layers, so given how limited it is used at the moment, the author thinks it makes sense for its usage to be removed, and code instead ported to a future async-compatible model.

### Backwards Compatibility

* Existing addons/scripts using mutable/blocking APIs will continue to function unchanged if the shared recursive locking data model is considered.
* They would need to modified otherwise, using the GIL-based locking model, and for FreeCAD API calls to be done in a scheduled main thread callback. 

## Open Issues

* **Signal Emission Threading Strategy**: Choose between worker-thread signal emission with UI scheduling or deferring all signal dispatch to the main thread.
* **Data Synchronization Model**: Decide on the long-term locking approach—continued GIL-based blocking, Qt event filtering, or fine-grained recursive locking—and the appropriate granularity of locks on data model classes.

## Rejected Ideas

* **Immutable data model with mutation queue**: Adopting an immutable FreeCAD core with a message queue for all state changes would require rewriting fundamental APIs and updating the entire ecosystem (add-ons, scripts, workbenches) to interact via queued commands. This approach is too foundational for the initial asynchronous infrastructure.
* **Coroutine-based data model**: Rewriting FreeCAD’s core to use an `async`/`await` coroutine paradigm would necessitate extensive changes across Python and C++ APIs and require all existing extensions to be ported to the new async model.

## Implementation

A proof-of-concept async recompute model using GIL-based locking approach exists, even though it does not solve all the issues presented here yet. Additional implementation work is being done to further experiment with shared recursive locking data model.

## FAQ

**Q:** Will users need to change scripts?

**A:** Maybe, but mainly for more advanced use cases, depending on the data and synchronization model chosen.

## Changelog

### 0.1 - 2025-05-20

* Initial version sent as draft for feedback

## References

* FreeCAD FPA grant proposal #36: [https://github.com/FreeCAD/FPA-grant-proposals/issues/36](https://github.com/FreeCAD/FPA-grant-proposals/issues/36)
* James Stanley ComputationDialog/long-running ops abort PR: [https://github.com/FreeCAD/FreeCAD/pull/19796](https://github.com/FreeCAD/FreeCAD/pull/19796)

## License / Copyright

All FEPs are explicitly [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
