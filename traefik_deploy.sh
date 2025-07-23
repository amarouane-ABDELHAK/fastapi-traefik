helm install --namespace=traefik --create-namespace traefik traefik/traefik \
  --set ports.web.port=80 \
  --set ports.websecure.port=443

