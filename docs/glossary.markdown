---
layout: page
title: Glossary
permalink: /glossary/
---
**Agreement:** See [Consensus](#consensus).

<a name="asynchronous"></a>**Asynchronous Environment:** In an asynchronous environment there are no bounds on timing. In an asynchronous environment clocks run arbitrarily fast, network communication takes arbitrarily long, and [state machines](#sm) take arbitrarily long to transition in response to an operation. Because there is no bound on timing for delivering and processing messages, it is impossible for other processes to know for certain that a process has failed or is being very very slow. The term "asynchronous" as used in the context of Paxos should not be confused with non-blocking operations on objects; they are often called asynchronous as well.

<a name="availability"></a> **Availability:** A request that is sent to a machine in a distributed system may become idle if the machine is unavailable for any reason. In the worst case, the request can be delayed until the problem is fixed or the faulty machine is replaced by a replica. Availability is the ability of a distributed system to limit this latency as much as possible. For a distributed system to be available, it should also be [reliable](#reliability).

<a name="bf"></a> **Byzantine Failure:** A [state machine](#sm) has experienced a byzantine failure if it behaved in an arbitrary manner, which includes sending fake messages, not sending any messages, trying to disrupt the computation, corrupting their local state and processing requests incorrectly among other unspecified transitions. [Paxos](#paxos) does not solve the [consensus](#consensus) problem in the existence of byzantine failures.

<a name="consensus"></a> **Consensus:** In the consensus problem, each process proposes some initial value, and processes that do not fail must reach an irrevocable decision on exactly one of the proposed values. The consensus problem captures an essential component of replication in distributed systems: the fact that replicas (processes) need to agree on the next state transition they handle, so that they can remain in identical states. [Paxos](#paxos) solves the consensus problem in an asynchronous environment, where processes can crash. But Paxos (much like any other consensus protocol) is limited by the [FLP Impossibility Result](#flp) in its ability to reach consensus in an asynchronous environment where processes can crash.

<a name="consistency"></a> **Consistency:** Distributed systems replicate shared state to improve fault tolerance, data availability and performance. However, if the updates to this state are not carefully controlled, the state on different replicas might diverge over time creating inconsistency between replicas. In this case two clients that read the state from two different replicas might see two different states. To prevent this every distributed system supports a consistency model, i.e. employs a protocol that supports a consistency model. Different consistency models offer different consistency guarantees, but as long as the user follows the rules associated with a consistency model, the distributed system guarantees that the user will not observe any inconsistencies. The most intuitive type of consistency is strong consistency. A protocol supports strong consistency, if all state changes are seen by all distributed processes in the same order, sequentially. [Paxos](#paxos) supports strong consistency.

<a name="cf"></a> **Crash Failure:** A [state machine](#sm) has experienced a crash failure if it will make no more transitions and thus its current state is fixed indefinitely. A crashed state machine does not make unspecified transitions. For machines that make unspecified transitions, see [Byzantine failures](#bf).

<a name="dsm"></a> **Deterministic State Machine:** In a deterministic state machine for any state and operation, the transition enabled by the operation is unique and the output is a function only of the state and the operation. Logically, a deterministic state machine handles one operation at a time.

<a name="fs"></a> **Fail-Stop:** A machine [crash](#cf) is fail-stop if other machines can detect reliably that the process has crashed. In an [asynchronous](#asynchronous) environment, one machine cannot tell whether another machine is slow or has crashed.

<a name="ft"></a> **Fault Tolerance:** See [Reliability](#reliability).

<a name="flp"></a> **FLP Impossibility Result:** "Consensus problem is not solvable in an asynchronous system." The result has been established by Fischer-Lynch-Paterson, hence the name FLP. The result states that there exists no deterministic algorithm that solves [consensus](#consensus) in an [asynchronous](#asynchronous) environment with reliable channels if one single process may [crash](#cf). This is due to the fact that in an asynchronous environment it is impossible to detect if a process has crashed or is very very slow. The basic idea behind the proof presented in the [FLP paper](httpss://groups.csail.mit.edu/tds/papers/Lynch/pods83-flp.pdf) is to show circumstances under which the protocol remains forever indecisive.

<a name="quorum"></a> **Majority:** See [Quorum](#quorum).

<a name="paxos"></a>**Paxos:** A [consensus](#consensus) protocol for [state machine replication](#smr) in an [asynchronous](#asynchronous) environment that admits [crash failures](#cf).

<a name="quorum"></a> **Quorum:** One way of achieving [consensus](#consensus) in a distributed system is using voting. A quorum is the minimum number of votes that a replica has to obtain in order to be allowed to perform a state transition in a distributed system. There are two rules about determining quorums in a distributed system. First, any two quorums must intersect in at least one process. Second, at least one of the quorums (which ones is unknown) contains processes that never crash. This guarantees that if a replica received votes from a quorum there will always be at least one process that voted for the replica and is not crashed. A simple example of quorums is the following. There are *n* processes, of which fewer than *n/2* are allowed to crash. Quorums then are all sets that have *^[n+1]^⁄~2~* processes.

<a name="reliability"></a>**Reliability:** The ability of a distributed system to deliver its services even when one or several of its software of hardware components fail. Reliability is one of the main expected advantages of a distributed system: In a distributed setting a machine affected by a failure can always be replaced by another one, and not prevent the completion of a request. An immediate and obvious consequence is that reliability relies on redundancy of both the software components and the state, which is achieved by [replication](#replication).

<a name="replication"></a> **Replication:** Maintaining multiple copies of state on replicated machines in a distributed system to achieve [fault tolerance](#ft). Replication increases fault tolerance, availability and performance but introduces [consistency](#consistency) issues. When same state is copied on different servers it should be kept consistent to give the illusion of a single state.

<a name="scalability"></a> **Scalability:** The ability of a system to continuously evolve in order to support a growing amount of tasks.

<a name="sm"></a> **State Machine:** An abstract machine that consists of a collection of states, a collection of transitions between states, and a current state. A transition to a new current state happens in response to an issued operation and produces an output. Transitions from the current state to the same state are allowed, and are used to model read-only operations.

<a name="smr"></a> **State Machine Replication (SMR):** A technique used in distributed systems to mask failures, and [crash failures](#cf) in particular. A collection of [replicas](#replication) of a [deterministic state machine](#dsm) are created. The replicas are then provided with the same sequence of operations, so they go through the same sequence of state transitions and end up in the same state and produce the same sequence of outputs. This way consistency between replicas is achieved. It is assumed that at least one replica never crashes, but we do not know a priori which replica this is.

**Synchronous Environment:** In a synchronous environment there are bounds on timing. In a synchronous system there is a bound on the transmission delay of messages, and a bound on the relative speed of processes. This allows accurate failure detection.

## References

-   [Paxos Wikipedia Page](https://en.wikipedia.org/wiki/Paxos_(computer_science))

-   [Leslie Lamport. 1978. Time, Clocks, and the Ordering of Events in a Distributed System. Commun. ACM 21, 7 (July 1978), 558--565.](https://research.microsoft.com/en-us/um/people/lamport/pubs/time-clocks.pdf)
-   [Richard D. Schlichting and Fred B. Schneider. 1983. Fail-stop Processors: An Approach to Designing Fault-tolerant Computing Systems. ACM Transactions on Computer Systems 1, 3 (Aug. 1983), 222--238.](httpss://www.cs.cornell.edu/fbs/publications/Fail_Stop.pdf)
-   [Fred B. Schneider. 1990. Implementing Fault-tolerant Services Using the State Machine Approach: A Tutorial. Comput. Surveys 22, 4 (Dec. 1990), 299--319.](httpss://www.cs.cornell.edu/fbs/publications/SMSurvey.pdf)
-   [Leslie Lamport. 1998. The Part-time Parliament. ACM Transactions on Computer Systems 16, 2 (May 1998), 133--169.](https://research.microsoft.com/en-us/um/people/lamport/pubs/lamport-paxos.pdf)
[](https://research.microsoft.com/en-us/um/people/lamport/pubs/lamport-paxos.pdf)
-   [](https://research.microsoft.com/en-us/um/people/lamport/pubs/lamport-paxos.pdf)[Roberto De Prisco, Butler W. Lampson, and Nancy Lynch. 2000. Revisiting the PAXOS Algorithm. Theoretical Computer Science 243, 1-2 (July 2000), 35--91.](https://research.microsoft.com/en-us/um/people/blampson/60-PaxosAlgorithm/Acrobat.pdf)
-   [Leslie Lamport. 2001. Paxos Made Simple. ACM SIGACT News (Distributed Computing Column) 32, 4 (2001), 51--58.](https://research.microsoft.com/en-us/um/people/lamport/pubs/paxos-simple.pdf)
-   [Butler W. Lampson. 2001. The ABCD's of Paxos. In Proceedings of the Twentieth Annual ACM Symposium on Principles of Distributed Computing (PODC '01). ACM, New York, NY, 13--14.](https://research.microsoft.com/en-us/um/people/blampson/65-ABCDPaxos/Acrobat.pdf)
-   [Eli Gafni and Leslie Lamport. 2003. Disk Paxos. Distributed Computing 16, 1 (Feb. 2003), 1--20.](https://dl.acm.org/citation.cfm?id=1061989)
-   [Leslie Lamport and Mike Massa. 2004. Cheap Paxos. In Proceedings of the 2004 International Conference on Dependable Systems and Networks (DSN '04). IEEE Computer Society, Washington, DC, 307--315.](https://research.microsoft.com/pubs/64634/web-dsn-submission.pdf?q=cheap)
-   [Leslie Lamport. 2005. Generalized Consensus and Paxos. Technical Report MSR-TR-2005-33. Microsoft Research, Mountain View, CA.](https://research.microsoft.com/pubs/64631/tr-2005-33.pdf)
-   [Leslie Lamport. 2006. Fast Paxos. Distributed Computing 19, 2 (October 2006), 79--103.](https://research.microsoft.com/pubs/64624/tr-2005-112.pdf)
-   [Leslie Lamport, Dahlia Malkhi, and Lidong Zhou. 2008. Stoppable Paxos. Technical Report. Microsoft Research, Mountain View, CA.](https://research.microsoft.com/apps/pubs/default.aspx?id=101826)
-   [Leslie Lamport, Dahlia Malkhi, and Lidong Zhou. 2009. Vertical Paxos and Primary-Backup Replication. In Proceedings of the Twenty-Eighth ACM Symposium on Principles of Distributed Computing (PODC '09). ACM, New York, NY, 312--313.](https://research.microsoft.com/pubs/80907/podc09v6.pdf)

Note that this is an incomplete list. For more references, you can refer to the
[Paxos Made Moderately Complex](/paper/) paper.
