start:
	docker build -t app:latest -f k8s/Dockerfile .
	minikube image load app:latest
	kubectl apply -f k8s/env-configmap.yaml
	kubectl apply -f k8s/db-statefulset.yaml
	kubectl apply -f k8s/db-service.yaml
	kubectl wait pod -l app=db --for=condition=ready --timeout=60s

	kubectl delete job app-migrations --ignore-not-found
	kubectl apply -f k8s/migrations/app-migrations.yaml
	kubectl wait job/app-migrations --for=condition=complete --timeout=60s

	kubectl apply -f k8s/
	kubectl wait pod -l app=app --for=condition=ready --timeout=60s
	kubectl port-forward service/app 8000:8000

logs:
	kubectl logs -f -l app=app

status:
	kubectl get pods
	kubectl get svc
	
delete:
	kubectl delete all,configmap,pvc --all
