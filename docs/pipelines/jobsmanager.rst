.. _jobsmanager:

===========
Job Manager
===========

This is a Reactor that can receive and handle event messages for all jobs,
regardless of owner or sender. It uses ``ManagedPipelineJobInstance``
internally to accomplish this work. The Reactor and its usage are documented
in detail in the :doc:`reactors_pipelinejobs_rx` section.
