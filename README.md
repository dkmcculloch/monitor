# monitor
You are responsible for monitoring a web property for changes, the first proof of concept is a simple page monitor.  The requirements are:
1) Log to a file the changed/unchanged state of the URL http://www.oracle.com/index.html.
2) Retry a configurable number of times in case of connection oriented errors.
3) Handle URL content change or unavailability as a program error with a non-zero exit.
4) Any other design decisions are up to the implementer.  Bonus for solid design and extensibility.
