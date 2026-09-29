# Orion Reports

The reports application provides record browsing, attachment access, summaries, documents, and member administration. It imports Orion Shared directly into its process using the immutable revision in requirements.txt.

Signed Orion sessions identify the user and tenant. Records belong to individual tenants. Member-role administration is reserved for administrators. Session verification uses SESSION_SIGNING_KEY; the record database and attachment directory are configured through RECORD_DATABASE and ATTACHMENT_ROOT.
