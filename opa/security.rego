package kubernetes.security

deny contains msg if {
  input.kind == "NetworkPolicy"
  not input.spec.ingress
  msg := "Deny-all NetworkPolicy detected"
}

deny contains msg if {
  input.kind == "NetworkPolicy"
  some i
  input.spec.ingress[i].from[_].podSelector.matchLabels == {}
  msg := "Allow-all ingress detected"
}
