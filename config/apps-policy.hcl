# Read-only permit
path "kv-v1/dev/testsecret" {
  capabilities = [ "read", "update", "list" ]
}
