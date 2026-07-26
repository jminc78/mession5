pipeline {
  agent any

  environment {
    COMPOSE_PROJECT_NAME = 'mission5'
  }

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Ensure models') {
      steps {
        sh '''
          set -e
          need_sync=0
          for task in qa generation summary; do
            if [ ! -f "backend/outputs/$task/final/model.safetensors" ]; then
              need_sync=1
            fi
          done

          if [ "$need_sync" = "1" ]; then
            SRC="${MODEL_SRC:-}"
            if [ -z "$SRC" ]; then
              for cand in \
                "/models/mission3" \
                "../mission3/outputs" \
                "../../mission3/outputs" \
                "/Users/jeongtaegoon/Desktop/ai_shift_track_project/mission3/outputs"
              do
                if [ -f "$cand/qa/final/model.safetensors" ]; then
                  SRC="$cand"
                  break
                fi
              done
            fi

            if [ -z "$SRC" ] || [ ! -d "$SRC" ]; then
              echo "ERROR: model.safetensors 가 없습니다."
              echo "backend/outputs/*/final 을 채우거나 MODEL_SRC 를 지정하세요."
              exit 1
            fi

            echo "Sync models from $SRC"
            for task in qa generation summary; do
              mkdir -p "backend/outputs/$task"
              rm -rf "backend/outputs/$task/final"
              cp -R "$SRC/$task/final" "backend/outputs/$task/final"
            done
          else
            echo "Models already present"
          fi

          ls -lh backend/outputs/*/final/model.safetensors
        '''
      }
    }

    stage('Build images') {
      steps {
        sh 'docker compose -f docker-compose.yaml build'
      }
    }

    stage('Deploy local') {
      steps {
        sh '''
          docker compose -f docker-compose.yaml up -d --remove-orphans
          docker compose -f docker-compose.yaml ps
        '''
      }
    }

    stage('Smoke check') {
      steps {
        sh '''
          set +e
          for i in 1 2 3 4 5 6 7 8 9 10 11 12; do
            if curl -fsS "http://host.docker.internal:8005/api/health" >/dev/null 2>&1; then
              echo "OK: app responds on host.docker.internal:8005"
              curl -fsS "http://host.docker.internal:8005/api/health"
              exit 0
            fi
            if curl -fsS "http://127.0.0.1:8005/api/health" >/dev/null 2>&1; then
              echo "OK: app responds on 127.0.0.1:8005"
              curl -fsS "http://127.0.0.1:8005/api/health"
              exit 0
            fi
            echo "waiting for app... ($i/12)"
            sleep 10
          done
          echo "Smoke check failed"
          docker compose -f docker-compose.yaml logs --tail=100 backend nginx
          exit 1
        '''
      }
    }
  }

  post {
    success {
      echo 'Deployed: http://127.0.0.1:8005'
    }
    failure {
      echo 'Deploy failed — check docker compose logs'
    }
  }
}
