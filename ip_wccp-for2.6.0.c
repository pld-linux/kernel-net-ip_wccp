/*
 *      $Id$
 *
 * Glenn Chisholm <glenn@ircache.net>
 *
 * Change log:
 *   2003-10-28 Alexander V. Lukyanov <lav@netis.ru>
 *              Updated to linux-2.6.0. Removed support for older kernels.
 *
 *   2003-10-20 Henrik Nordstrom <hno@squid-cache.org>
 *   		Dropped support for old kernels. Linux-2.4 or later required
 *   		Play well with Netfilter
 *
 *   2002-04-16 francis a. vidal <francisv@dagupan.com>
 *		Module license tag
 *
 *   2002-04-13 Henrik Nordstrom <hno@squid-cache.org>
 *   		Updated to Linux-2.4
 *		- there no longer is a len argument to ip_wccp_recv
 *		- deal with fragmented skb packets
 *		- incremental checksumming to allow detection of corrupted
 *		  packets
 *
 *   1999-09-30 Glenn Chisholm <glenn@ircache.net>
 *              Original release
 */

#include <linux/config.h>
#include <linux/module.h>
#include <linux/types.h>
#include <linux/sched.h>
#include <linux/kernel.h>
#include <linux/skbuff.h>
#include <linux/netdevice.h>
#include <linux/in.h>
#include <linux/if_arp.h>
#include <linux/init.h>
#include <linux/inetdevice.h>
#include <linux/version.h>
#include <net/checksum.h>
#include <net/protocol.h>
#include <linux/netfilter_ipv4.h>
#include <net/ip.h>
#include <net/inet_ecn.h>

#define WCCP_PROTOCOL_TYPE 	0x883E
#define WCCP_GRE_LEN		4

MODULE_AUTHOR("Glenn Chisholm");
MODULE_DESCRIPTION("WCCP module");
MODULE_LICENSE("GPL");

static inline void ip_wccp_ecn_decapsulate(struct iphdr *outer_iph, struct sk_buff *skb)
{
	struct iphdr *inner_iph = skb->nh.iph;

	if (INET_ECN_is_ce(outer_iph->tos) &&
	    INET_ECN_is_not_ce(inner_iph->tos))
		IP_ECN_set_ce(inner_iph);
}


int ip_wccp_rcv(struct sk_buff *skb)
{
	u32  *gre_hdr;
	struct iphdr *iph;

	if (!pskb_may_pull(skb, 16))
		goto drop;

	iph = skb->nh.iph;
	gre_hdr = (u32 *)skb->h.raw;
	if(*gre_hdr != __constant_htonl(WCCP_PROTOCOL_TYPE))
		goto drop;

	skb->mac.raw = skb->nh.raw;
	skb->nh.raw = pskb_pull(skb, WCCP_GRE_LEN);
	memset(&(IPCB(skb)->opt), 0, sizeof(struct ip_options));
	skb->protocol = __constant_htons(ETH_P_IP);
	skb->pkt_type = PACKET_HOST;

	dst_release(skb->dst);
	skb->dst = NULL;
#ifdef CONFIG_NETFILTER
	nf_conntrack_put(skb->nfct);
	skb->nfct = NULL;
#ifdef CONFIG_NETFILTER_DEBUG
	skb->nf_debug = 0;
#endif
#endif
	ip_wccp_ecn_decapsulate(iph, skb);
	netif_rx(skb);
	return(0);

drop:
	kfree_skb(skb);
	return(0);
}

static struct inet_protocol ipgre_protocol = {
	.handler	=	ip_wccp_rcv,
};

int __init ip_wccp_init(void)
{
	printk(KERN_INFO "WCCP IPv4/GRE driver\n");
	inet_add_protocol(&ipgre_protocol, IPPROTO_GRE);
	return 0;
}

static void __exit ip_wccp_fini(void)
{
	if ( inet_del_protocol(&ipgre_protocol, IPPROTO_GRE) < 0 )
		printk(KERN_INFO "ipgre close: can't remove protocol\n");
	else
		printk(KERN_INFO "WCCP IPv4/GRE driver unloaded\n");
}

#ifdef MODULE
module_init(ip_wccp_init);
#endif
module_exit(ip_wccp_fini);
