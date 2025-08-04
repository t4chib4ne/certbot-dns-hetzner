# Hetzner DNS Certbot Plugin

Certbot authentication plugin for dns-01 validation via Hetzner.

## Notice

If your are looking for a fully functional and more battle tested Hetzner plugin for Certbot please consider using [ctrlaltcoop/certbot-dns-hetzner](https://github.com/ctrlaltcoop/certbot-dns-hetzner) instead of this project. This project was created for my own educational purposes and aims to be as simple as possible for easy auditing. It is public for easier access on my servers.

## Installation

If you are on Gentoo you can use [tachibane-overlay](https://github.com/t4chib4ne/tachibane-overlay):

```shell
# eselect repository add tachibane git https://github.com/t4chib4ne/tachibane-overlay
# emaint sync -r tachibane
# emerge --ask app-crypt/certbot-dns-hetzner::tachibane
```

For any other distro you can simply clone this repo, change to it and run the following

```shell
# pip install .
```

Running this outside of a virtual environment is not recommended.

## Usage

Please see the output of

```shell
$ certbot help dns-hetzner
```

For a general guide on obtaining certificates with Certbot please read the officical documentation.
