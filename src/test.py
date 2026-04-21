#!/usr/bin/env python

from certbot_dns_hetzner.api_hetzner import Hetzner

token = input("Please insert your Hetzner Cloud API Token: ")
domain = input("Please specify your domain: ")
domain = f"_acme-challenge.{domain}"

client = Hetzner(token)

client.create_txt_record(domain, "this is a test")
input("Can you see it?")

client.delete_txt_record(domain)
input("Is it gone?")
