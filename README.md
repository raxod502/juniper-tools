# Juniper Networks '19-20 tools and scripts

For our '19-20 Clinic project, we worked on two separate projects, the
*fragmentation project* and the *benchmarking project*. The code for
the fragmentation project is available in the following two places:

* The [`fragmentation`](fragmentation) subdirectory of this project,
  for the tools and scripts used to set up and test things.
* The
  [`juniper`](https://github.com/raxod502/juniper-linux/tree/juniper)
  branch of [our fork of the Linux
  kernel](https://github.com/raxod502/juniper-linux), which contains
  the code implementing our changes. The relevant patch is also
  available in this repository at
  [`fragmentation/juniper.patch`](fragmentation/juniper.patch).

The code for the benchmarking project does not yet include changes to
the Linux kernel, so it is fully self-contained under
[`benchmarking`](benchmarking).
