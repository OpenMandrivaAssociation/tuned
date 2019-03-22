%global __requires_exclude /usr/bin/stap

Summary:	A dynamic adaptive system tuning daemon
Name:		tuned
Version:	2.11.0
Release:	1
License:	GPLv2+
URL:		https://github.com/redhat-performance/tuned
Group:		System/Kernel and hardware
Source0:	https://github.com/redhat-performance/tuned/archive/%{name}-%{version}.tar.gz
Patch0:		0002-get-CPE-string-from-etc-os-release-rather-than-the-m.patch  
Patch5:		tuned-2.4.1-dont-start-in-virtual-env.patch
BuildArch:	noarch
Requires(post):	virt-what
BuildRequires:	systemd-macros
BuildRequires:	pkgconfig(python3)
BuildRequires:	python3egg(six)
Requires:	python3egg(decorator)
Requires:	python3egg(configobj)
Requires:	python3egg(pyudev)
Requires:	python3egg(six)
Requires:	python3egg(python-linux-procfs)
Requires:	python3-dbus
Requires:	python-gi
Requires:	virt-what
Requires:	hdparm
Requires:	ethtool
Requires:	typelib(GObject)
Requires:	dbus
Requires:	polkit
%ifnarch %{armx}
Requires:	cpupower
Requires:	x86_energy_perf_policy
%endif
%if %{mdvver} > 3000000
%rename		laptop-mode-tools
%endif

%description
The tuned package contains a daemon that tunes system settings dynamically.
It does so by monitoring the usage of several system components periodically.
Based on that information components will then be put into lower or higher
power saving modes to adapt to the current usage. Currently only ethernet
network and ATA harddisk devices are implemented.

%package	gtk
Summary:	GTK GUI for tuned
Requires:	%{name} = %{version}-%{release}
Requires:	powertop
Requires:	polkit
Requires:	python-gi

%description	gtk
GTK GUI that can control tuned and provide simple profile editor.

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
%autosetup -p1

%build

%install
%make_install
rm -r %{buildroot}%{_docdir}/%{name}

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-tuned.preset << EOF
enable tuned.service
EOF

%post
if [ ! -f %{_sysconfdir}/tuned/active_profile ] || [ -z "$(cat %{_sysconfdir}/tuned/active_profile 2>/dev/null)" ]; then
    PROFILE="$(%{_sbindir}/tuned-adm recommend 2>/dev/null)"
    [ "$PROFILE" ] || PROFILE=balanced
    %{_sbindir}/tuned-adm profile "$PROFILE" 2>/dev/null || printf '%s\n' "$PROFILE" > %{_sysconfdir}/tuned/active_profile
fi

# convert active_profile from full path to name (if needed)
sed -e 's|.*/\([^/]\+\)/[^\.]\+\.conf|\1|' -i %{_sysconfdir}/tuned/active_profile

%systemd_post %{name}

%files
%doc AUTHORS README doc/TIPS.txt
%{_datadir}/bash-completion/completions/tuned-adm
%exclude %{python3_sitelib}/tuned/gtk
%{python3_sitelib}/tuned
%{_sbindir}/tuned
%{_sbindir}/tuned-adm
%exclude %{_prefix}/lib/tuned/default
%exclude %{_prefix}/lib/tuned/desktop-powersave
%exclude %{_prefix}/lib/tuned/laptop-ac-powersave
%exclude %{_prefix}/lib/tuned/server-powersave
%exclude %{_prefix}/lib/tuned/laptop-battery-powersave
%exclude %{_prefix}/lib/tuned/enterprise-storage
%exclude %{_prefix}/lib/tuned/spindown-disk
%exclude %{_mandir}/man7/tuned-profiles-compat.7*
%{_prefix}/lib/tuned
%{_prefix}/lib/kernel/install.d/*tuned.*
%dir %{_sysconfdir}/tuned
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/tuned/active_profile
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/tuned/profile_mode
%config(noreplace) %{_sysconfdir}/tuned/tuned-main.conf
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/tuned/bootcmdline
%config(noreplace) %{_sysconfdir}/tuned/cpu-partitioning-variables.conf
%config(noreplace) %{_sysconfdir}/tuned/realtime-variables.conf
%config(noreplace) %{_sysconfdir}/tuned/realtime-virtual-guest-variables.conf
%config(noreplace) %{_sysconfdir}/tuned/realtime-virtual-host-variables.conf
%config(noreplace) %{_sysconfdir}/tuned/sap-hana-vmware-variables.conf
%{_sysconfdir}/dbus-1/system.d/com.redhat.tuned.conf
%verify(not size mtime md5) %{_sysconfdir}/modprobe.d/tuned.conf
%{_tmpfilesdir}/tuned.conf
%{_unitdir}/tuned.service
%{_presetdir}/86-tuned.preset
%{_libexecdir}/tuned/defirqaffinity.py
%dir %{_libexecdir}/tuned/__pycache__
%{_libexecdir}/tuned/__pycache__/defirqaffinity.*

%dir %{_localstatedir}/log/tuned
%dir /run/tuned
%{_mandir}/man5/tuned*
%{_mandir}/man7/tuned-profiles*
%{_mandir}/man8/tuned*
%{_sysconfdir}/grub.d/00_tuned
%{_datadir}/polkit-1/actions/com.redhat.tuned.policy

%files gtk
%{_sbindir}/tuned-gui
%{python_sitelib}/tuned/gtk
%{_datadir}/tuned/ui
%{_iconsdir}/hicolor/scalable/apps/tuned.svg
%{_datadir}/applications/tuned-gui.desktop

%files utils
%{_bindir}/powertop2tuned
%{_libexecdir}/tuned/pmqos-static*
%{_libexecdir}/tuned/__pycache__/pmqos-static*

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
%{_mandir}/man7/tuned-profiles-compat.7*
