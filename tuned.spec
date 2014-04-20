Summary:	A dynamic adaptive system tuning daemon
Name:		tuned
Version:	2.3.0
%define	gitdate	20140306
Release:	4.%{gitdate}.1
License:	GPLv2+
Source0:	https://fedorahosted.org/releases/t/u/tuned/%{name}-%{version}.tar.xz
URL:		https://fedorahosted.org/tuned/
Group:		System/Kernel and hardware
BuildArch:	noarch
Requires(post):	virt-what
Requires:	pythonegg(decorator) python-dbus python-gi pythonegg(pyudev)
Requires:	virt-what pythonegg(configobj) cpupower
Patch0:		0001-specify-what-dbus-interface-to-use-for-dbus-methods.patch
Patch1:		0002-get-CPE-string-from-etc-os-release-rather-than-the-m.patch  
Patch2:		0003-fix-install-locations-of-tmpfiles-bash-completion.patch

%description
The tuned package contains a daemon that tunes system settings dynamically.
It does so by monitoring the usage of several system components periodically.
Based on that information components will then be put into lower or higher
power saving modes to adapt to the current usage. Currently only ethernet
network and ATA harddisk devices are implemented.

%package	utils
Requires:	%{name} = %{EVRD}
Summary:	Various tuned utilities
Group:		System/Kernel and hardware
Requires:	powertop

%description	utils
This package contains utilities that can help you to fine tune and
debug your system and manage tuned profiles.

%package	utils-systemtap
Summary:	Disk and net statistic monitoring systemtap scripts
Requires:	%{name} = %{EVRD}
Group:		System/Kernel and hardware
Requires:	systemtap

%description	utils-systemtap
This package contains several systemtap scripts to allow detailed
manual monitoring of the system. Instead of the typical IO/sec it collects
minimal, maximal and average time between operations to be able to
identify applications that behave power inefficient (many small operations
instead of fewer large ones).

%package	profiles-compat
Summary:	Additional tuned profiles mainly for backward compatibility with tuned 1.0
Group:		System/Kernel and hardware
Requires:	%{name} = %{EVRD}

%description profiles-compat
Additional tuned profiles mainly for backward compatibility with tuned 1.0.
It can be also used to fine tune your system for specific scenarios.

%prep
%setup -q
%apply_patches

%build

%install
%makeinstall_std
rm -r %{buildroot}%{_docdir}/%{name}

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-tuned.preset << EOF
enable tuned.service
EOF

%post
# try to autodetect the best profile for the system in case there is none preset
if [ ! -f %{_sysconfdir}/tuned/active_profile -o -z "`cat %{_sysconfdir}/tuned/active_profile 2>/dev/null`" ]
then
	PROFILE=`%{_sbindir}/tuned-adm recommend 2>/dev/null`
	[ "$PROFILE" ] || PROFILE=balanced
	%{_sbindir}/tuned-adm profile "$PROFILE" 2>/dev/null || echo -n "$PROFILE" > %{_sysconfdir}/tuned/active_profile
fi

# convert active_profile from full path to name (if needed)
sed -e 's|.*/\([^/]\+\)/[^\.]\+\.conf|\1|' -i %{_sysconfdir}/tuned/active_profile

%files
%doc AUTHORS README doc/TIPS.txt
%{_datadir}/bash-completion/completions/tuned
%{python_sitelib}/tuned
%{_sbindir}/tuned
%{_sbindir}/tuned-adm
%exclude %{_prefix}/lib/tuned/default
%exclude %{_prefix}/lib/tuned/desktop-powersave
%exclude %{_prefix}/lib/tuned/laptop-ac-powersave
%exclude %{_prefix}/lib/tuned/server-powersave
%exclude %{_prefix}/lib/tuned/laptop-battery-powersave
%exclude %{_prefix}/lib/tuned/enterprise-storage
%exclude %{_prefix}/lib/tuned/spindown-disk
%{_prefix}/lib/tuned
%dir %{_sysconfdir}/tuned
%config(noreplace) %{_sysconfdir}/tuned/active_profile
%config(noreplace) %{_sysconfdir}/tuned/tuned-main.conf
%{_sysconfdir}/dbus-1/system.d/com.redhat.tuned.conf
%{_tmpfilesdir}/tuned.conf
%{_unitdir}/tuned.service
%{_presetdir}/86-tuned.preset

%dir %{_localstatedir}/log/tuned
%dir /run/tuned
%{_mandir}/man5/tuned*
%{_mandir}/man8/tuned*

%files utils
%{_bindir}/powertop2tuned
%{_libexecdir}/tuned/pmqos-static*

%files utils-systemtap
%doc doc/README.utils
%doc doc/README.scomes
%{_sbindir}/varnetload
%{_sbindir}/netdevstat
%{_sbindir}/diskdevstat
%{_sbindir}/scomes
%{_mandir}/man8/varnetload.*
%{_mandir}/man8/netdevstat.*
%{_mandir}/man8/diskdevstat.*
%{_mandir}/man8/scomes.*

%files profiles-compat
%{_prefix}/lib/tuned/default
%{_prefix}/lib/tuned/desktop-powersave
%{_prefix}/lib/tuned/laptop-ac-powersave
%{_prefix}/lib/tuned/server-powersave
%{_prefix}/lib/tuned/laptop-battery-powersave
%{_prefix}/lib/tuned/enterprise-storage
%{_prefix}/lib/tuned/spindown-disk

%changelog
* Sat Apr 20 2014 Per Øyvind Karlsen <proyvind@moondrake.org> 2.3.0-4.20140306.1
- make sure to specify which interface on the DBus bus for the methods to use
- update to latest code from git snapshot
- fix paths for tmpfiles & bash-completions
- adapt to cooker

* Thu Mar  6 2014 Jaroslav Škarvada <jskarvad@redhat.com> - 2.3.0-3
- added kernel-tools requirement
  resolves: rhbz#1072981

* Fri Nov  8 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 2.3.0-2
- fixed race condition in the start/stop code
  resolves: rhbz#1028119
- improved tuned responsiveness
  resolves: rhbz#1028122

* Wed Nov  6 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 2.3.0-1
- new-release
  resolves: rhbz#1020743
  - audio plugin: fixed audio settings in standard profiles
    resolves: rhbz#1019805
  - video plugin: fixed tunings
  - daemon: fixed crash if preset profile is not available
    resolves: rhbz#953128
  - man: various updates and corrections
  - functions: fixed usb and bluetooth handling
  - tuned: switched to lightweighted pygobject3-base
  - daemon: added global config for dynamic_tuning
    resolves: rhbz#1006427
  - utils: added pmqos-static script for debug purposes
    resolves: rhbz#1015676
  - throughput-performance: various fixes
    resolves: rhbz#987570
  - tuned: added global option update_interval
  - plugin_cpu: added support for x86_energy_perf_policy
    resolves: rhbz#1015675
  - dbus: fixed KeyboardInterrupt handling
  - plugin_cpu: added support for intel_pstate
    resolves: rhbz#996722
  - profiles: various fixes
    resolves: rhbz#922068
  - profiles: added desktop profile
    resolves: rhbz#996723
  - tuned-adm: implemented non DBus fallback control
  - profiles: added sap profile
  - tuned: lowered CPU usage due to python bug
    resolves: rhbz#917587

* Tue Mar 19 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 2.2.2-1
- new-release:
  - cpu plugin: fixed cpupower workaround
  - cpu plugin: fixed crash if cpupower is installed

* Fri Mar  1 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 2.2.1-1
- new release:
  - audio plugin: fixed error handling in _get_timeout
  - removed cpupower dependency, added sysfs fallback
  - powertop2tuned: fixed parser crash on binary garbage
    resolves: rhbz#914933
  - cpu plugin: dropped multicore_powersave as kernel upstream already did
  - plugins: options manipulated by dynamic tuning are now correctly saved and restored
  - powertop2tuned: added alias -e for --enable option
  - powertop2tuned: new option -m, --merge-profile to select profile to merge
  - prefer transparent_hugepage over redhat_transparent_hugepage
  - recommend: use recommend.conf not autodetect.conf
  - tuned.service: switched to dbus type service
    resolves: rhbz#911445
  - tuned: new option --pid, -P to write PID file
  - tuned, tuned-adm: added new option --version, -v to show version
  - disk plugin: use APM value 254 for cleanup / APM disable instead of 255
    resolves: rhbz#905195
  - tuned: new option --log, -l to select log file
  - powertop2tuned: avoid circular deps in include (one level check only)
  - powertop2tuned: do not crash if powertop is not installed
  - net plugin: added support for wake_on_lan static tuning
    resolves: rhbz#885504
  - loader: fixed error handling
  - spec: used systemd-rpm macros
    resolves: rhbz#850347

* Mon Jan 28 2013 Jan Vcelak <jvcelak@redhat.com> 2.2.0-1
- new release:
  - remove nobarrier from virtual-guest (data loss prevention)
  - devices enumeration via udev, instead of manual retrieval
  - support for dynamically inserted devices (currently disk plugin)
  - dropped rfkill plugins (bluetooth and wifi), the code didn't work

* Wed Jan  2 2013 Jaroslav Škarvada <jskarvad@redhat.com> - 2.1.2-1
- new release:
  - systemtap {disk,net}devstat: fix typo in usage
  - switched to configobj parser
  - latency-performance: disabled THP
  - fixed fd leaks on subprocesses

* Thu Dec 06 2012 Jan Vcelak <jvcelak@redhat.com> 2.1.1-1
- fix: powertop2tuned execution
- fix: ownership of /etc/tuned

* Mon Dec 03 2012 Jan Vcelak <jvcelak@redhat.com> 2.1.0-1
- new release:
  - daemon: allow running without selected profile
  - daemon: fix profile merging, allow only safe characters in profile names
  - daemon: implement missing methods in DBus interface
  - daemon: implement profile recommendation
  - daemon: improve daemonization, PID file handling
  - daemon: improved device matching in profiles, negation possible
  - daemon: various internal improvements
  - executables: check for EUID instead of UID
  - executables: run python with -Es to increase security
  - plugins: cpu - fix cpupower execution
  - plugins: disk - fix option setting
  - plugins: mounts - new, currently supports only barriers control
  - plugins: sysctl - fix a bug preventing settings application
  - powertop2tuned: speedup, fix crashes with non-C locales
  - powertop2tuned: support for powertop 2.2 output
  - profiles: progress on replacing scripts with plugins
  - tuned-adm: bash completion - suggest profiles from all supported locations
  - tuned-adm: complete switch to D-bus
  - tuned-adm: full control to users with physical access

* Mon Oct 08 2012 Jaroslav Škarvada <jskarvad@redhat.com> - 2.0.2-1
- New version
- Systemtap scripts moved to utils-systemtap subpackage

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jun 12 2012 Jaroslav Škarvada <jskarvad@redhat.com> - 2.0.1-3
- another powertop-2.0 compatibility fix
  Resolves: rhbz#830415

* Tue Jun 12 2012 Jan Kaluza <jkaluza@redhat.com> - 2.0.1-2
- fixed powertop2tuned compatibility with powertop-2.0

* Tue Apr 03 2012 Jaroslav Škarvada <jskarvad@redhat.com> - 2.0.1-1
- new version

* Fri Mar 30 2012 Jan Vcelak <jvcelak@redhat.com> 2.0-1
- first stable release
