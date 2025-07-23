password=$(htpasswd -nbBC 10 "" 'password1234' | tr -d ':\n' | sed 's/^..//')


helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

helm install argocd argo/argo-cd \
  --namespace argocd --create-namespace \
  --set configs.secret.argocdServerAdminPassword="$2y$10$..." \
  --set server.service.type=NodePort
