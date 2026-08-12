---
title: Gradle "Unable to establish loopback connection" on Windows - launch the daemon on JDK 8
tags: [gradle, java, windows, jvm, sockets]
projects: [blanket]
date: 2026-07-29
---

## Problem

Every Gradle invocation fails immediately, before any task runs:

```
FAILURE: Build failed with an exception.
* What went wrong:
java.io.IOException: Unable to establish loopback connection
```

The daemon log (`~/.gradle/daemon/<version>/daemon-*.out.log`) shows the daemon binding
its TCP port fine, then dying when it accepts the first connection:

```
[ERROR] org.gradle.internal.remote.internal.inet.TcpIncomingConnector - Could not accept remote connection.
Caused by: java.io.IOException: Unable to establish loopback connection
Caused by: java.net.SocketException: Invalid argument: connect
	at java.base/sun.nio.ch.UnixDomainSockets.connect0(Native Method)
	at java.base/sun.nio.ch.PipeImpl$Initializer$LoopbackConnector.run(PipeImpl.java:132)
```

Fails identically on JDK 17, 21, and 25. Plain TCP loopback works (a hand-written
`ServerSocket`/`Socket` on 127.0.0.1 connects), so it is NOT a firewall blocking the port.

## Root cause

The JVM's NIO `Pipe`/`Selector` implementation (used internally by Gradle's message
plumbing, not by any port you can see) switched to **Unix-domain sockets on Windows in
JDK 16+**. On a machine where the AF_UNIX stack is broken/disabled, `UnixDomainSockets.connect0`
throws `SocketException: Invalid argument`, so the JVM can't create its own internal
loopback pipe - the failure has nothing to do with Gradle's daemon TCP port.

JDK 8's `PipeImpl` predates the AF_UNIX change and uses a TCP-loopback pipe, which works.

## Solution

Launch Gradle on a **JDK 8** runtime (the *launcher* JVM only - module toolchains are
unaffected and still resolved separately):

```powershell
$env:JAVA_HOME = 'C:\Program Files\Eclipse Adoptium\jdk-8.0.482.8-hotspot'
.\gradlew.bat <tasks>
```

If your project's toolchains require a newer JDK to *compile*, keep them pinned per-module
(`languageVersion = JavaLanguageVersion.of(21)`) and let Gradle's toolchain detection find
them - only the launcher needs to be 8. Works because launcher JVM and toolchain JVM are
independent.

## Notes

- Confirm the diagnosis by running a two-line `ServerSocket`+`Socket` loopback test under
  the *failing* JDK: it will also throw `Invalid argument` from `UnixDomainSockets` if a
  `Pipe.open()`/`Selector.open()` is involved, while a pure TCP socket succeeds.
- A sandboxed/locked-down shell can block the daemon's loopback socket too and fail the
  same way even on JDK 8 - run Gradle unsandboxed.
- The permanent fix is repairing the Windows AF_UNIX stack; the JDK 8 launcher is the
  reliable workaround.
