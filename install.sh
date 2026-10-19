#!/bin/bash
# Statping installation script for Linux, Mac, and maybe Windows.
#
# This installation script is a modification of Yarn's installation
set -e

reset="\033[0m"
red="\033[31m"
green="\033[32m"
yellow="\033[33m"
cyan="\033[36m"
white="\033[37m"
gpg_key=64B9C6AAE2D55278
gpgurl=https://statping.com/statping.gpg
repo=https://github.com/Gevroska/statping-ng

statping_get_tarball() {
  fext='tar.gz'
  if [ ${OS} == 'windows' ]; then
    fext='zip'
    ARCH='x64'
  fi
  url="$repo/releases/latest/download/statping-$1-$2.$fext"
  printf "$cyan> Downloading latest version for $OS $ARCH...\n$url $reset\n"
  # Get both the tarball and its GPG signature
  tarball_tmp=`mktemp -t statping.tar.gz.XXXXXXXXXX`
  if curl --fail -L -s -o "$tarball_tmp" "$url"; then
    # All this dance is because `tar --strip=1` does not work everywhere
    temp=$(mktemp -d statping.XXXXXXXXXX)
    if [ ${OS} == 'windows' ]; then
      unzip $tarball_tmp -d "$temp"
    else
      tar xzf $tarball_tmp -C "$temp"
    fi
    printf "$green> Installing to $DEST/statping-ng\n"
    mv "$temp"/statping "$DEST"
    rm -rf "$temp"
    rm $tarball_tmp*
    printf "$cyan> Statping-ng is now installed! $reset\n"
    printf "$white>   Repo:     $repo $reset\n"
    printf "$white>   Wiki:     $repo/wiki $reset\n"
    printf "$white>   Issues:   $repo/issues $reset\n"
    printf "$cyan> Try to run \"statping help\" $reset\n"
  else
    printf "$red> Failed to download $url.$reset\n"
    exit 1;
  fi
}

statping_reset() {
  unset -f statping_install statping_reset statping_get_tarball statping_verify_or_quit getOS getArch
}

statping_install() {
  printf "${white}Installing Statping-ng!$reset\n"
  getOS
  getArch
  statping_get_tarball $OS $ARCH
  statping_reset
}

statping_verify_or_quit() {
  read -p "$1 [y/N] " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]
  then
    printf "$red> Aborting$reset\n"
    exit 1
  fi
}

# get the users operating system
getOS() {
    OS="`uname`"
    case $OS in
      'Linux')
        OS='linux'
        DEST=/usr/local/bin
        alias ls='ls --color=auto'
        ;;
      'FreeBSD')
        OS='freebsd'
        DEST=/usr/local/bin
        alias ls='ls -G'
        ;;
      'OpenBSD')
        OS='openbsd'
        DEST=/usr/local/bin
        alias ls='ls -G'
        ;;
      'WindowsNT')
        OS='windows'
        DEST=/usr/local/bin
        ;;
      'MINGW*')
        OS='windows'
        DEST=/usr/local/bin
        ;;
      'CYGWIN*')
        OS='windows'
        DEST=/usr/local/bin
        ;;
      'Darwin')
        OS='darwin'
        DEST=/usr/local/bin
        ;;
      'SunOS')
        OS='linux'
        DEST=/usr/local/bin
        ;;
      'AIX') ;;
      *) ;;
    esac
}

# get 64x or 32 machine arch
getArch() {
    MACHINE_TYPE=`uname -m`
    if [ ${MACHINE_TYPE} == 'x86_64' ]; then
      ARCH="amd64"
    elif [ ${MACHINE_TYPE} == 'arm' ]; then
      ARCH="arm"
    elif [ ${MACHINE_TYPE} == 'arm64' ]; then
      ARCH="arm64"
    elif [ ${MACHINE_TYPE} == 'aarch64' ]; then
      ARCH="arm64"
    else
      ARCH="386"
    fi
}

cd ~
statping_install $1 $2
