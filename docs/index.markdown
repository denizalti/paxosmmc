---
layout: page
---

**Paxos** algorithms are a family of consensus algorithms (or protocols) that are used in distributed systems to achieve consensus in the presence of crash failures.
These protocols are infamously difficult to understand, mainly due to the various states that have to be maintained on servers that have varying roles in the execution of the
protocol.
Paxos consensus protocols are generally used to implement strongly-consistent replication in distributed systems that run on asynchronous environments.

In this website, we explain how the Paxos protocols work using easy to understand invariants and code. It is easy to understand because the states that are maintained
by servers with different roles are shown explicitly and the correctness of the state changes are described using invariants that hold before and after the state changes.
In addition, a high-level and complete [Python implementation]](/code/) is provided.

* [Why is Paxos used in distributed systems?](/why/)
* [How does Paxos work?](/how/)
* [When does Paxos work? What are the limitations and practical issues of Paxos?](/when/)

<br>
The content on this website is based on our Computing Surveys paper. You can access the published full paper, [Paxos Made Moderately Complex](/paper/), which also covers many Paxos variants and provides Exercises to aid in learning the intricacies of Paxos.
<br>
<br>
<br>

This website is built and maintained by [Deniz Altınbüken, Ph.D.](https://denizaltinbuken.com) If you have questions, you can contact me at [hello@{{ site.address }}](mailto:hello@{{ site.address }})
