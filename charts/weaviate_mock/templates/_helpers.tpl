{{/*
Expand the name of the chart.
*/}}
{{- define "weaviate-mock.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "weaviate-mock.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "weaviate-mock.labels" -}}
helm.sh/chart: {{ include "weaviate-mock.name" . }}
app.kubernetes.io/name: {{ include "weaviate-mock.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "weaviate-mock.selectorLabels" -}}
app.kubernetes.io/name: {{ include "weaviate-mock.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}