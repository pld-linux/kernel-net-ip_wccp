/*
 *      $Id$
 *
 * Glenn Chisholm <glenn@ircache.net>
 *
 * Change log:
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
#include <asm/uaccess.h>
#include <linux/skbuff.h>
#include <linux/netdevice.h>
#include <linux/in.h>
#include <linux/if_arp.h>
#include <linux/init.h>
#include <linux/inetdevice.h>
#include <linux/netfilter_ipv4.h>
#include <net/ip.h>
#include <net/inet_ecn.h>

#include <net/ip.h>

#define WCCP_PROTOCOL_TYPE 	0x883E
#define WCCP_GRE_LEN		sizeof(u32)

#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,4,9)
/* New License scheme */
#ifdef MODULE_LICENSE
MODULE_AUTHOR("Glenn Chisholm");
MODULE_DESCRIPTION("WCCP module");
MODULE_LICENSE("GPL");
#endif
#endif

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
	u8   *h;
	struct iphdr *iph;

	if (!pskb_may_pull(skb, 16))
		goto drop;

	iph = skb->nh.iph;
	gre_hdr = (u32 *)skb->h.raw;
	h = skb->data;
	if(*gre_hdr != htonl(WCCP_PROTOCOL_TYPE)) 
		goto drop;

	skb->mac.raw = skb->nh.raw;
	skb->nh.raw = pskb_pull(skb, WCCP_GRE_LEN);
	memset(&(IPCB(skb)->opt), 0, sizeof(struct ip_options));
	skb->protocol = htons(ETH_P_IP);
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
  ip_wccp_rcv,     
  NULL,           
  0,            
  IPPROTO_GRE, 
  0,          
  NULL,      
  "GRE"     
};

int __init ip_wccp_init(void)
{
	printk(KERN_INFO "WCCP IPv4/GRE driver\n");
	inet_add_protocol(&ipgre_protocol);
	return 0;
}

static void __exit ip_wccp_fini(void)
{
	if ( inet_del_protocol(&ipgre_protocol) < 0 )
		printk(KERN_INFO "ipgre close: can't remove protocol\n");
	else
		printk(KERN_INFO "WCCP IPv4/GRE driver unloaded\n");
}

#ifdef MODULE
module_init(ip_wccp_init);
#endif
module_exit(ip_wccp_fini);
