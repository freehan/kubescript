## Introduction

This folder contains a sample ingress setup on GCP. The following steps demonstrated a live seamless migration from classic non-NEG setup to a NEG setup. Please refer to the (official doc)[https://cloud.google.com/kubernetes-engine/docs/how-to/container-native-load-balancing] for more detail. 

## STEP 0: Initialize Non-NEG setup 
```
kubectl apply -f hostname.yaml
kubectl apply -f ing1.yaml	
```

- Wait for sufficient time
- Verify by sending requests and get continous 200 responses with no 500s.
- Start sending traffic to `/foo` and `/bar` in order to hit different backends.

## STEP 1: Setup NEG backends
```
kubectl apply -f hostname-neg.yaml
kubectl apply -f ing2.yaml	
```

- Wait for sufficient time
- Validate/Monitor the following setup:
  - Get NEG-status: `kubectl get svc foo-backend-neg -o yaml | grep neg-status` Same for `bar-backend-neg` service
  - NEGs config and Endpoints in NEG: `gcloud compute network-endpoint-groups list-network-endpoints ${NETWORK_ENDPOINT_GROUP_NAME}`
  - backend-services health status: `gcloud compute backend-services get-health ${BACKEND_SERVICE_NAME}`
  - URLmap: `gcloud compute url-maps describe ${INGRESS_URL_MAP_NAME}`
  - Traffic responses from `/foo` and `/bar`. This can be done via stackdriver LB access log. 


## STEP 2: Swap NEG backends
```
kubectl apply -f ing3.yaml	
```

- Wait for sufficient time
- Validate setup (Same with Step 1)


## STEP 3: Remove Non-NEG backends
```
kubectl apply -f ing4.yaml	
```

- Wait for sufficient time
- Validate setup (Same with Step 1)
