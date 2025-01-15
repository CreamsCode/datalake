# MongoDB Cluster Deployment with Terraform and GitHub Actions

## Descripción
Este repositorio despliega un clúster de MongoDB en AWS usando Terraform y un pipeline CI/CD en GitHub Actions.

## Requisitos
- Cuenta de AWS
- Terraform instalado
- Configuración de secretos en GitHub:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`

## Instrucciones
1. Clona este repositorio.
2. Configura tus credenciales de AWS como secretos en GitHub.
3. Modifica las variables en `variables.tf` si es necesario.
4. Haz un push a la rama `main` para iniciar el pipeline.
