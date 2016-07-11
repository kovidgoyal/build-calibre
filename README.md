Build the calibre installers, including all dependencies from scratch
=======================================================================

This repository contains code to automate the process of building calibre,
including all its dependencies, from scratch, for all platforms that calibre
supports. 

In general builds proceed in two steps, first build all the dependencies, then
build the calibre installer itself.

Requirements
---------------

First you need a *bootstrapped* copy of the calibre source code. This means
either untar the official calibre source distribution tarball, or checkout
calibre from github and run `python setup.py bootstrap`.

Then set the environment variable `CALIBRE_SRC_DIR` to point to the location of
the calibre source code.

The code in this repository is intended to run on linux.

To make the linux calibre builds, it uses docker.

To make the Windows and OS X builds it uses VirtualBox VMs. Instructions on
creating the VMs are in their respective sections below.

Linux
-------

You need to have docker installed and running as the linux
builds are done in a docker container.

To build the 64bit and 32bit dependencies for calibre, run:

```
./linux 64
./linux 32
```

The output (after a very long time) will be in `build/linux[32|63]`

Now you can build calibre itself using these dependencies, to do that, run:

```
CALIBRE_SRC_DIR=/whatever ./linux 64 calibre
CALIBRE_SRC_DIR=/whatever ./linux 32 calibre
```

The output will be `build/linux[32|64]/calibre-*.txz` which are the linux
binary installers for calibre.


OS X
------

You need a VirtualBox virtual machine of OS X 10.9 (Mavericks) named
`osx-calibre-build`. To setup the VM, follow the steps

  * Turn on Remote Login under Network (SSHD)
  * Create a user account named `kovid` and enable password-less login for SSH
    for that account (setup `~/.ssh/authorized_keys`)
  * Setup ssh into the VM from the host under the name: `osx-calibre-build`
  * Setup passwordless sudo in the Virtual Machine for the user account kovid
  * Install XCode (version 6.2 is the latest that runs on Mavericks). Download
    from https://developer.apple.com/download/more/
    Note that installing only the command line tools is not sufficient as Qt
    requires the full XCode.
  * Run `sudo mkdir -p /calibre /scripts /sources /sw /patches && sudo chown kovid:staff /calibre /scripts /sources /sw /patches`

To build the dependencies for calibre, run:

```
./osx
```

The output (after a very long time) will be in `build/osx`

Now you can build calibre itself using these dependencies, to do that, run:

```
CALIBRE_SRC_DIR=/whatever ./osx calibre
```

The output will be `build/osx/calibre-*.dmg` which is the OS X
binary installer for calibre.


Windows
------------

You need a VirtualBox virtual machine of Windows 7 64bit named
`win-calibre-build`. To setup the VM, follow the steps

    * Install Visual Studio Community Edition 2015 with all the C++ development
      tools, including XP support. Be sure to start Visual Studio at least
      once.
    * Install cmake: https://cmake.org/download/
    * Install perl: http://www.activestate.com/activeperl
    * Install ruby: http://rubyinstaller.org/
    * Install python2: https://www.python.org/downloads/
    * Install SVN: http://tortoisesvn.net/downloads.html
    * Install nasm.exe:  http://www.nasm.us/pub/nasm/releasebuilds/2.11/win32/nasm-2.11-win32.zip
    * Install git: https://git-scm.com/download/win
    * Ensure that all the above tools are in PATH so that they can be run in a
      command prompt using just their names.
    * Create the folders: C:\sw C:\sources C:\patches C:\scripts C:\calibre C:\t
    * Install cygwin, with the: vim, dos2unix, rsync, openssh, unzip, wget, make, zsh, bash-completion, curl
      packages
    * Edit /etc/passwd and replace all occurrences of /bin/bash with /bin/zsh (in
      a cygwin prompt)

    * Setup a password for your windows user account
    * Follow the steps here:
      http://pcsupport.about.com/od/windows7/ht/auto-logon-windows-7.htm to allow the
      machine to bootup without having to enter the password

    * The following steps must all be run in an administrator cygwin shell, to
      enable SSH logins to the machine

    * First clean out any existing cygwin ssh setup with::
        net stop sshd
        cygrunsrv -R sshd
        net user sshd /DELETE
        net user cyg_server /DELETE (delete any other cygwin users account you
        can list them with net user)
        rm -R /etc/ssh*
        mkpasswd -cl > /etc/passwd
        mkgroup --local > /etc/group
    * Assign the necessary rights to the normal user account (administrator
      cygwin command prompt needed - editrights is available in \cygwin\bin)::
        editrights.exe -a SeAssignPrimaryTokenPrivilege -u kovid
        editrights.exe -a SeCreateTokenPrivilege -u kovid
        editrights.exe -a SeTcbPrivilege -u kovid
        editrights.exe -a SeServiceLogonRight -u kovid
    * Run::
        ssh-host-config
      And answer (yes) to all questions. If it asks do you want to use a
      different user name, specify the name of your user account and enter
      username and password 
    * On Windows XP, I also had to run::
        passwd -R
      to allow sshd to use my normal user account even with public key
      authentication. See http://cygwin.com/cygwin-ug-net/ntsec.html for
      details. On Windows 7 this wasn't necessary for some reason.
    * Start sshd with::
        net start sshd
    * See http://www.kgx.net.nz/2010/03/cygwin-sshd-and-windows-7/ for details
