/*
 *      $Id$
 *
 * Glenn Chisholm <glenn@ircache.net>
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

#include <net/ip.h>

#define WCCP_PROTOCOL_TYPE 	0x883E
#define WCCP_GRE_LEN		sizeof(long)

int ip_wccp_rcv(struct sk_buff *skb, unsigned short len)
{
	long *gre_hdr;

	gre_hdr = (unsigned long *)skb->h.raw;
	if(*gre_hdr != htonl(WCCP_PROTOCOL_TYPE)) 
		goto drop;

	skb->mac.raw = skb->nh.raw;
	skb->nh.raw = skb_pull(skb, skb->h.raw + WCCP_GRE_LEN - skb->data);

	if (skb->len <= 0) 
                goto drop;

	memset(&(IPCB(skb)->opt), 0, sizeof(struct ip_options));
	skb->protocol = __constant_htons(ETH_P_IP);
	skb->pkt_type = PACKET_HOST;
	skb->ip_summed = 0;
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
