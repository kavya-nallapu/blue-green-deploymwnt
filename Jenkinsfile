pipeline {
  agent any

  environment {
    AWS_REGION = "ap-south-1"
    AWS_ACCOUNT_ID = "123456789012"
    ECR_REPO = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/myapp"
    K8S_NS = "prod"
    APP_CONTAINER = "myapp"
    IMAGE_TAG = "${BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Test') {
      steps {
        sh '''
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pytest -q
        '''
      }
    }

    stage('Build & Push Image') {
      steps {
        sh '''
          aws ecr get-login-password --region $AWS_REGION | \
            docker login --username AWS --password-stdin $ECR_REPO

          docker build -t $ECR_REPO:$IMAGE_TAG .
          docker push $ECR_REPO:$IMAGE_TAG
        '''
      }
    }

    stage('Detect Active/Inactive Color') {
      steps {
        script {
          def active = sh(
            script: "kubectl -n $K8S_NS get svc myapp-active -o jsonpath='{.spec.selector.version}'",
            returnStdout: true
          ).trim()

          env.ACTIVE_COLOR = active
          env.INACTIVE_COLOR = (active == "blue") ? "green" : "blue"

          echo "ACTIVE=${env.ACTIVE_COLOR}, INACTIVE=${env.INACTIVE_COLOR}"
        }
      }
    }

    stage('Deploy Inactive Color') {
      steps {
        sh '''
          kubectl -n $K8S_NS set image deployment/myapp-$INACTIVE_COLOR \
            $APP_CONTAINER=$ECR_REPO:$IMAGE_TAG

          kubectl -n $K8S_NS rollout status deployment/myapp-$INACTIVE_COLOR --timeout=240s
        '''
      }
    }

    stage('Smoke Test Inactive') {
      steps {
        sh '''
          kubectl -n $K8S_NS run smoke-test --rm -i --restart=Never \
            --image=curlimages/curl:8.8.0 -- \
            curl -fsS http://myapp-$INACTIVE_COLOR:8000/health
        '''
      }
    }

    stage('Switch Traffic') {
      steps {
        sh '''
          kubectl -n $K8S_NS patch svc myapp-active \
            -p '{"spec":{"selector":{"app":"myapp","version":"'"$INACTIVE_COLOR"'"}}}'
        '''
      }
    }

    stage('Post Switch Check') {
      steps {
        sh '''
          sleep 10
          curl -fsS https://myapp.example.com/health
        '''
      }
    }
  }

  post {
    failure {
      sh '''
        if [ -n "$ACTIVE_COLOR" ]; then
          kubectl -n $K8S_NS patch svc myapp-active \
            -p '{"spec":{"selector":{"app":"myapp","version":"'"$ACTIVE_COLOR"'"}}}' || true
        fi
      '''
    }
  }
}
