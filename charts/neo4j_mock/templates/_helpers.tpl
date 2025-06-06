{{/*
Expand the name of the chart.
*/}}
{{- define "neo4j-mock.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "neo4j-mock.fullname" -}}
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
{{- define "neo4j-mock.labels" -}}
helm.sh/chart: {{ include "neo4j-mock.name" . }}
app.kubernetes.io/name: {{ include "neo4j-mock.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "neo4j-mock.selectorLabels" -}}
app.kubernetes.io/name: {{ include "neo4j-mock.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}