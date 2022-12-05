/**
 * This file is part of the dionaea honeypot
 *
 * SPDX-FileCopyrightText: 2009 Paul Baecher & Markus Koetter
 *
 * SPDX-License-Identifier: GPL-2.0-or-later
 */

#ifndef HAVE_UTIL_H
#define HAVE_UTIL_H

#include <stdbool.h>
#include <stdint.h>

#ifndef s6_addr32
#define s6_addr32 __u6_addr.__u6_addr32
#endif

void *ADDROFFSET(const void *x);
unsigned int ADDRSIZE(const void *x);
void *PORTOFFSET(const void *x);

bool sockaddr_storage_from(struct sockaddr_storage *ss, int family, void *host, uint16_t port);
bool parse_addr(char const * const addr, char const * const iface, uint16_t const port, struct sockaddr_storage * const sa, int * const socket_domain, socklen_t * const sizeof_sa);

int ipv6_addr_linklocal(struct in6_addr const * const a);
int ipv6_addr_v4mapped(struct in6_addr const * const a);

struct tempfile
{
	int fd;
	FILE *fh;
	char *path;
};

struct tempfile *tempfile_new(char *path, char *prefix);
struct tempfile *tempdownload_new(char *prefix);
void tempfile_close(struct tempfile *tf);
void tempfile_unlink(struct tempfile *tf);
void tempfile_free(struct tempfile *tf);

#endif
