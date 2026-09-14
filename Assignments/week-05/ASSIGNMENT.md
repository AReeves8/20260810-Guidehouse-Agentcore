# Week 5 Assignment: Deploy a Flask App to ECS by Hand

## Objective
A Flask application, running as a container on ECS Fargate in your own AWS
account, reachable over the public internet on the task's public IP, returning
a successful response from a `/health` endpoint.

## Requirements

### The application
1. A Flask app with a **`GET /health` endpoint that returns HTTP 200**. The
   response body can be anything — `{"status": "ok"}` is fine.
2. **Suggested:** use the `fieldnotes` app from Week 5's demos. It already has
   `/health`, `/ready`, and a working `Dockerfile`, so you can spend your time
   on AWS rather than on Python.
   **You may use any Flask app you like**, including one you write from scratch
   for this — a single file with one route is completely acceptable. The
   assignment is about the deployment, not the app.
3. The app must listen on **`0.0.0.0`**, not `127.0.0.1`. A container that
   binds to localhost is reachable only from inside itself, and this is the
   single most common reason a task looks healthy and refuses connections.

### The deployment
4. Build the image and push it to a **private ECR repository** in your account.
5. Create an **ECS cluster** running on **Fargate**.
6. Create a **task definition** that runs your image, exposes the port your app
   listens on, and has a working **task execution role** (ECS needs it to pull
   from ECR and write logs).
7. Run the app as an **ECS service** with a desired count of 1.
8. The task must be placed in a **public subnet with a public IP assigned**,
   and its **security group must allow inbound TCP on your app's port**.
9. **Do not use a load balancer.** Hit the task's public IP directly.
10. Confirm it works from your own machine by hitting the endpoint with `curl`, Postman, or in your browser.

### Clean up when you are finished
11. **Take your screenshots before you tear down.** See the `Deliverable` section for more info.
12. **Delete what you created**, in this order: set the service's desired count
    to 0 and delete the service, delete the cluster, then delete the ECR
    repository (and the RDS instance, if you did the optional step). A running
    Fargate task and an idle RDS instance both bill by the hour whether or not
    anyone is using them.


## Optional extra: connect it to RDS

Only attempt this once the basic deployment is working and you have your
screenshots. It is genuinely optional and does not affect completion.

- Create a small **RDS PostgreSQL** instance (`db.t4g.micro` is plenty).
- Pass the connection string to your container as an environment variable —
  or, better, store it in **Secrets Manager** and reference it from the task
  definition's `secrets` block, as Thursday's demo did.
- Configure the security groups so the **RDS instance accepts inbound 5432
  from the ECS task's security group** — referencing the security group rather
  than an IP range, since a Fargate task's IP changes every time it restarts.
- Verify the connection. If you are using `fieldnotes`, its **`/ready`**
  endpoint returns 200 only when the database is actually reachable, and 503
  otherwise — so a successful `/ready` is your proof.

## Deliverable
**Four screenshots**, submitted on Canvas:

1. **The ECS cluster** — the Clusters list or your cluster's detail page,
   showing the cluster you created.
2. **The service** — showing it ACTIVE with 1 running task.
3. **The task's networking detail** — showing the assigned **public IP**.
4. **The response** — a terminal or browser window showing a successful
   `/health` response, with the **URL/IP visible** and matching the IP in
   screenshot 3.

Screenshots 3 and 4 must show the **same IP address**. That pairing is what
demonstrates you reached your own running task rather than something else.

**If you completed the optional RDS step**, add a fifth screenshot showing a
successful `/ready` response (or your own equivalent proof that the app is
talking to the database).

Do not include your AWS account ID, access keys, or database password in any
screenshot — crop or redact them if they appear.

## Time expectation
~1.5–2 hours 
