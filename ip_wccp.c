/*
 *      $Id$
 *
 * Glenn Chisholm <glenn@ircache.net>
 *
 * Change log:
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
#include <net/checksum.h>

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

#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,4,0)
int ip_wccp_rcv(struct sk_buff *skb)
#else
int ip_wccp_rcv(struct sk_buff *skb, unsigned short len)
#endif
{
	u32  *gre_hdr;
	u8   *h;

#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,4,0)
	if (!pskb_may_pull(skb, 16))
		goto drop;
#endif

	gre_hdr = (u32 *)skb->h.raw;
	h = skb->data;
	if(*gre_hdr != htonl(WCCP_PROTOCOL_TYPE)) 
		goto drop;

	skb->mac.raw = skb->nh.raw;
#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,4,0)
	skb->nh.raw = pskb_pull(skb, WCCP_GRE_LEN);
#else /* old kernels */
	skb->nh.raw = skb_pull(skb, skb->h.raw + WCCP_GRE_LEN - skb->data);
	if (skb->len <= 0) 
                goto drop;
#endif
	memset(&(IPCB(skb)->opt), 0, sizeof(struct ip_options));
	skb->protocol = __constant_htons(ETH_P_IP);
	skb->pkt_type = PACKET_HOST;
#if LINUX_VERSION_CODE >= KERNEL_VERSION(2,4,0)
	if (skb->ip_summed == CHECKSUM_HW)
		skb->csum = csum_sub(skb->csum,
				     csum_partial(skb->mac.raw, skb->nh.raw-skb->mac.raw, 0));
#else
	skb->ip_summed = 0;
#endif
	dst_release(skb->dst);
	skb->dst = NULL;

	return ip_rcv(skb, skb->dev, NULL);

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

int init_module(void) 
{
	printk(KERN_INFO "WCCP IPv4/GRE driver\n");
	inet_add_protocol(&ipgre_protocol);
	return 0;
}

void cleanup_module(void)
{
	if ( inet_del_protocol(&ipgre_protocol) < 0 )
		printk(KERN_INFO "ipgre close: can't remove protocol\n");
	else
		printk(KERN_INFO "WCCP IPv4/GRE driver unloaded\n");
}
