# NetworkPolicy FQDN Limitation

Standard Kubernetes NetworkPolicy operates primarily with Pod selectors,
namespace selectors, IP blocks, protocols and ports.

It does not provide portable standard FQDN-based rules such as:

- allow only github.com
- allow only ghcr.io

Project 6 therefore permits required CI external HTTPS egress on TCP 443
while documenting that this is broader than true domain-level filtering.

More advanced FQDN-aware controls require networking functionality beyond
standard Kubernetes NetworkPolicy.
