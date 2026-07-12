{{/*
Expand the name of the chart.
*/}}
{{- define "property-service.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "property-service.fullname" -}}
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

{{- define "property-service.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "property-service.labels" -}}
helm.sh/chart: {{ include "property-service.chart" . }}
{{ include "property-service.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: property-service
environment: {{ .Values.environment }}
{{- end }}

{{- define "property-service.selectorLabels" -}}
app.kubernetes.io/name: {{ include "property-service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "property-service.apiLabels" -}}
{{ include "property-service.selectorLabels" . }}
app.kubernetes.io/component: api
{{- end }}

{{- define "property-service.workerLabels" -}}
{{ include "property-service.selectorLabels" . }}
app.kubernetes.io/component: worker
worker-queue: {{ .queue }}
{{- end }}

{{- define "property-service.image" -}}
{{- if .Values.global.imageRegistry -}}
{{- printf "%s/%s:%s" .Values.global.imageRegistry .repository .tag }}
{{- else -}}
{{- printf "%s:%s" .repository .tag }}
{{- end -}}
{{- end }}

{{- define "property-service.envFrom" -}}
- configMapRef:
    name: {{ include "property-service.fullname" . }}-config
- secretRef:
    name: {{ include "property-service.fullname" . }}-secrets
{{- end }}
