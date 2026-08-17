# Security Policy

## Legacy driver warning

openCUDA's core research involves hardware whose final vendor-supported driver/toolkit generations are legacy software. Wrapping or isolating an old driver does not make that driver current or eliminate its security risk.

The recommended deployment model for the K80 backend is a dedicated compute node with constrained network exposure, least-privilege service accounts, no untrusted multi-tenant workloads, and clear separation between the modern client environment and the legacy execution service.

## Reporting

Do not open a public issue for a vulnerability that would create immediate risk to users. Use GitHub's private vulnerability reporting feature if it is enabled for the repository; otherwise contact the repository owner privately.

## Supply-chain rules

- Do not commit NVIDIA driver/toolkit binaries or proprietary SDK archives.
- Download vendor components only from sources whose provenance can be verified.
- Pin CI actions to reviewed major versions initially and move toward commit pinning as the project matures.
- Treat code-generation, binary-translation, and dynamically loaded kernel paths as high-risk surfaces requiring bounds checks and input validation.
