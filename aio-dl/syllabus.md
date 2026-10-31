# Book 2 Syllabus

Complete Round 2 extension curriculum. Book 1 is a declared prerequisite dependency; no Book 1 content is duplicated here.

<!-- syllabus-canonical -->
```yaml
syllabus_version: 1
baseline:
  math:
  - algebra
  - functions-and-graphs
  - trigonometry-basics
  - limits
  - derivatives-1d
  - chain-rule-1d
  - integrals-1d
  - exponentials-and-logs
  python:
  - variables-and-types
  - lists-dicts-sets
  - control-flow
  - functions
  - classes-basics
  - file-io-basics
clusters:
- attention-transformers
- language-transformers
- cross-modal-vision
- probabilistic-latent-models
- generative-models
- capstone
imports:
  book: aio-ml
  units:
  - F1-scientific-python
  - F2-vectors
  - F4-matrices
  - F3-multivar-calculus
  - F5-probability
  - F6-svd-spectral
  - C1-ml-fundamentals
  - C2-linear-models
  - C3-gradient-descent
  - C6-neural-networks
  - C7-pytorch
  - C10-cnn-transfer
  - C5-embeddings
  - C9-dimensionality-reduction
  - C11-competition-craft
  - C8-neural-training
  - C12-classical-models
  concepts:
  - numpy-arrays
  - broadcasting
  - vectorization
  - elementwise-ops
  - aggregation-axis
  - random-seeding
  - dot-product
  - matrix-multiplication
  - expectation
  - variance
  - independence
  - variance-of-sums
  - torch-tensors
  - nn-module
  - requires-grad
  - tensor-shape-tracing
  - softmax
  - cross-entropy-loss
  - torch-optimizers
  - autograd-training
  - convolution
  - feature-maps
  - cnn-training
  - gradient
  - covariance
  - gaussian-distribution
  - sampling-simulation
  - conditional-probability
  - bayes-rule
  - eigenvalues-eigenvectors
  - spectral-decomposition
  - svd
  - train-test-split
  - mse-loss
  - relu-activation
  - mlp-architecture
  - pca
  - invertibility-via-rank
  - sum-of-squares-gradients
  - overfitting
  - accuracy-precision-recall
  - class-imbalance
  - linear-regression
  - l2-regularization
  - gradient-descent
  - learning-rate
  - stochastic-gd
  - parameter-counting
  - hidden-test-protocol
  - metric-driven-iteration
  - writeup-quality
  - colab-coding-submission
  - cpu-and-gpu-round-boundary
  - trained-mlp
  - k-means
  - lloyd-algorithm
evidence_imports:
  book: aio-ml
  concepts:
  - tokenization
  - word-embeddings
  - gensim-usage
  - embedding-matrices
  lesson_paths:
  - units/10-C5-embeddings/lessons/01-tokens-and-embeddings.ipynb
  practices:
  - C5-p01
  - C5-p02
  - C5-p05
  - C5-p06
  - C5-p12
  - C5-p13
  - C5-p15
  - C5-p17
  assessments:
  - r1-001-p05-1
  - r1-001-p05-2
  - r1-001-p05-3
  - r1-001-p05-4
concepts:
- id: matrix-transpose
  cluster: attention-transformers
- id: query-key-value-attention
  cluster: attention-transformers
- id: scaled-dot-product-attention
  cluster: attention-transformers
- id: attention-mask
  cluster: attention-transformers
- id: causal-self-attention
  cluster: attention-transformers
- id: multi-head-attention
  cluster: attention-transformers
- id: sinusoidal-positional-encoding
  cluster: attention-transformers
- id: attention-complexity
  cluster: attention-transformers
- id: transformer-residual-layernorm
  cluster: attention-transformers
- id: position-wise-feed-forward
  cluster: attention-transformers
- id: transformer-block
  cluster: attention-transformers
- id: embedding-model-training
  cluster: language-transformers
- id: learned-token-embedding
  cluster: language-transformers
- id: language-transformer
  cluster: language-transformers
- id: causal-language-modeling
  cluster: language-transformers
- id: masked-language-modeling
  cluster: language-transformers
- id: nlp-pretraining-objectives
  cluster: language-transformers
- id: nlp-fine-tuning-protocol
  cluster: language-transformers
- id: transformer-nlp-task-design
  cluster: language-transformers
- id: vision-transformers
  cluster: cross-modal-vision
- id: object-detection
  cluster: cross-modal-vision
- id: unet
  cluster: cross-modal-vision
- id: graph-neural-network-transformer-applications
  cluster: cross-modal-vision
- id: multivariate-gaussian
  cluster: probabilistic-latent-models
- id: kl-divergence
  cluster: probabilistic-latent-models
- id: autoencoder
  cluster: probabilistic-latent-models
- id: gaussian-reparameterization
  cluster: probabilistic-latent-models
- id: variational-autoencoder
  cluster: probabilistic-latent-models
- id: generative-adversarial-network
  cluster: generative-models
- id: denoising-diffusion-probabilistic-models
  cluster: generative-models
- id: stable-diffusion
  cluster: generative-models
- id: gpu-colab-l4-workflow
  cluster: capstone
- id: open-ended-experiment-design
  cluster: capstone
- id: open-ended-model-evaluation
  cluster: capstone
- id: semi-supervised-pseudo-labeling
  cluster: capstone
- id: scientific-ml-inverse-problems
  cluster: capstone
- id: mixture-parameter-regression
  cluster: capstone
units:
- id: B2-019-attention-transformers
  track: extension
  title: Attention and Transformer Mechanics
  book: 2
  layer: round-2-extension
  round: 2
  prereqs:
  - aio-ml:C7-pytorch
  - aio-ml:C10-cnn-transfer
  - aio-ml:C5-embeddings
  - aio-ml:C8-neural-training
  concept_prerequisites:
  - aio-ml:numpy-arrays
  - aio-ml:broadcasting
  - aio-ml:vectorization
  - aio-ml:elementwise-ops
  - aio-ml:aggregation-axis
  - aio-ml:random-seeding
  - aio-ml:dot-product
  - aio-ml:matrix-multiplication
  - aio-ml:expectation
  - aio-ml:variance
  - aio-ml:independence
  - aio-ml:variance-of-sums
  - aio-ml:torch-tensors
  - aio-ml:nn-module
  - aio-ml:requires-grad
  - aio-ml:tensor-shape-tracing
  - aio-ml:softmax
  - aio-ml:cross-entropy-loss
  - aio-ml:torch-optimizers
  - aio-ml:autograd-training
  teaches:
  - matrix-transpose
  - query-key-value-attention
  - scaled-dot-product-attention
  - attention-mask
  - causal-self-attention
  - multi-head-attention
  - sinusoidal-positional-encoding
  - attention-complexity
  - transformer-residual-layernorm
  - position-wise-feed-forward
  - transformer-block
  length: double
- id: B2-020-language-transformers
  track: extension
  title: Language Transformers
  book: 2
  layer: round-2-extension
  round: 2
  prereqs:
  - aio-ml:F1-scientific-python
  - aio-ml:F4-matrices
  - aio-ml:C7-pytorch
  - aio-ml:C10-cnn-transfer
  - aio-ml:C8-neural-training
  - B2-019-attention-transformers
  concept_prerequisites:
  - attention-mask
  - causal-self-attention
  - sinusoidal-positional-encoding
  - transformer-block
  - aio-ml:random-seeding
  - aio-ml:matrix-multiplication
  - aio-ml:torch-tensors
  - aio-ml:nn-module
  - aio-ml:requires-grad
  - aio-ml:tensor-shape-tracing
  - aio-ml:softmax
  - aio-ml:cross-entropy-loss
  - aio-ml:torch-optimizers
  - aio-ml:autograd-training
  teaches:
  - embedding-model-training
  - learned-token-embedding
  - language-transformer
  - causal-language-modeling
  - masked-language-modeling
  - nlp-pretraining-objectives
  - nlp-fine-tuning-protocol
  - transformer-nlp-task-design
  length: double
- id: B2-021-cross-modal-transformers-vision
  track: extension
  title: Cross-modal Transformers and Advanced Vision
  book: 2
  layer: round-2-extension
  round: 2
  prereqs:
  - aio-ml:F1-scientific-python
  - aio-ml:F4-matrices
  - aio-ml:C7-pytorch
  - aio-ml:C10-cnn-transfer
  - aio-ml:C8-neural-training
  - B2-019-attention-transformers
  - B2-020-language-transformers
  concept_prerequisites:
  - attention-mask
  - query-key-value-attention
  - multi-head-attention
  - attention-complexity
  - transformer-block
  - aio-ml:numpy-arrays
  - aio-ml:broadcasting
  - aio-ml:aggregation-axis
  - aio-ml:random-seeding
  - aio-ml:matrix-multiplication
  - aio-ml:torch-tensors
  - aio-ml:nn-module
  - aio-ml:requires-grad
  - aio-ml:tensor-shape-tracing
  - aio-ml:softmax
  - aio-ml:cross-entropy-loss
  - aio-ml:torch-optimizers
  - aio-ml:autograd-training
  - aio-ml:convolution
  - aio-ml:feature-maps
  - aio-ml:cnn-training
  teaches:
  - vision-transformers
  - object-detection
  - unet
  - graph-neural-network-transformer-applications
  length: double
- id: B2-022-probabilistic-latent-models
  track: extension
  title: Probabilistic Latent Models
  book: 2
  layer: round-2-extension
  round: 2
  prereqs:
  - aio-ml:F1-scientific-python
  - aio-ml:F4-matrices
  - aio-ml:F3-multivar-calculus
  - aio-ml:F5-probability
  - aio-ml:F6-svd-spectral
  - aio-ml:C1-ml-fundamentals
  - aio-ml:C2-linear-models
  - aio-ml:C6-neural-networks
  - aio-ml:C7-pytorch
  - aio-ml:C9-dimensionality-reduction
  - aio-ml:C8-neural-training
  - B2-021-cross-modal-transformers-vision
  concept_prerequisites:
  - aio-ml:numpy-arrays
  - aio-ml:broadcasting
  - aio-ml:aggregation-axis
  - aio-ml:random-seeding
  - aio-ml:matrix-multiplication
  - aio-ml:gradient
  - aio-ml:expectation
  - aio-ml:variance
  - aio-ml:covariance
  - aio-ml:gaussian-distribution
  - aio-ml:sampling-simulation
  - aio-ml:conditional-probability
  - aio-ml:bayes-rule
  - aio-ml:eigenvalues-eigenvectors
  - aio-ml:spectral-decomposition
  - aio-ml:svd
  - aio-ml:train-test-split
  - aio-ml:mse-loss
  - aio-ml:relu-activation
  - aio-ml:mlp-architecture
  - aio-ml:torch-tensors
  - aio-ml:nn-module
  - aio-ml:requires-grad
  - aio-ml:torch-optimizers
  - aio-ml:autograd-training
  - aio-ml:pca
  teaches:
  - multivariate-gaussian
  - kl-divergence
  - autoencoder
  - gaussian-reparameterization
  - variational-autoencoder
  length: double
- id: B2-023-generative-models-diffusion
  track: extension
  title: Generative Models and Diffusion
  book: 2
  layer: round-2-extension
  round: 2
  prereqs:
  - aio-ml:F1-scientific-python
  - aio-ml:F4-matrices
  - aio-ml:F3-multivar-calculus
  - aio-ml:F5-probability
  - aio-ml:C1-ml-fundamentals
  - aio-ml:C2-linear-models
  - aio-ml:C6-neural-networks
  - aio-ml:C7-pytorch
  - aio-ml:C8-neural-training
  - B2-019-attention-transformers
  - B2-020-language-transformers
  - B2-021-cross-modal-transformers-vision
  - B2-022-probabilistic-latent-models
  concept_prerequisites:
  - query-key-value-attention
  - learned-token-embedding
  - unet
  - multivariate-gaussian
  - gaussian-reparameterization
  - kl-divergence
  - autoencoder
  - variational-autoencoder
  - aio-ml:numpy-arrays
  - aio-ml:broadcasting
  - aio-ml:random-seeding
  - aio-ml:matrix-multiplication
  - aio-ml:gradient
  - aio-ml:expectation
  - aio-ml:variance
  - aio-ml:independence
  - aio-ml:variance-of-sums
  - aio-ml:covariance
  - aio-ml:gaussian-distribution
  - aio-ml:sampling-simulation
  - aio-ml:train-test-split
  - aio-ml:mse-loss
  - aio-ml:relu-activation
  - aio-ml:mlp-architecture
  - aio-ml:torch-tensors
  - aio-ml:nn-module
  - aio-ml:requires-grad
  - aio-ml:softmax
  - aio-ml:cross-entropy-loss
  - aio-ml:torch-optimizers
  - aio-ml:autograd-training
  teaches:
  - generative-adversarial-network
  - denoising-diffusion-probabilistic-models
  - stable-diffusion
  length: double
- id: B2-024-gpu-scientific-ml-capstone
  track: extension
  title: GPU Scientific Modeling Capstone
  book: 2
  layer: round-2-extension
  round: 2
  prereqs:
  - aio-ml:F1-scientific-python
  - aio-ml:F4-matrices
  - aio-ml:F3-multivar-calculus
  - aio-ml:F5-probability
  - aio-ml:C1-ml-fundamentals
  - aio-ml:C2-linear-models
  - aio-ml:C3-gradient-descent
  - aio-ml:C6-neural-networks
  - aio-ml:C7-pytorch
  - aio-ml:C10-cnn-transfer
  - aio-ml:C11-competition-craft
  - aio-ml:C8-neural-training
  - aio-ml:C12-classical-models
  - B2-023-generative-models-diffusion
  concept_prerequisites:
  - aio-ml:numpy-arrays
  - aio-ml:broadcasting
  - aio-ml:random-seeding
  - aio-ml:matrix-multiplication
  - aio-ml:invertibility-via-rank
  - aio-ml:gradient
  - aio-ml:sum-of-squares-gradients
  - aio-ml:expectation
  - aio-ml:variance
  - aio-ml:variance-of-sums
  - aio-ml:independence
  - aio-ml:covariance
  - aio-ml:gaussian-distribution
  - aio-ml:sampling-simulation
  - aio-ml:train-test-split
  - aio-ml:overfitting
  - aio-ml:accuracy-precision-recall
  - aio-ml:class-imbalance
  - aio-ml:linear-regression
  - aio-ml:mse-loss
  - aio-ml:l2-regularization
  - aio-ml:gradient-descent
  - aio-ml:learning-rate
  - aio-ml:stochastic-gd
  - aio-ml:relu-activation
  - aio-ml:mlp-architecture
  - aio-ml:torch-tensors
  - aio-ml:nn-module
  - aio-ml:requires-grad
  - aio-ml:parameter-counting
  - aio-ml:convolution
  - aio-ml:cnn-training
  - aio-ml:hidden-test-protocol
  - aio-ml:metric-driven-iteration
  - aio-ml:writeup-quality
  - aio-ml:colab-coding-submission
  - aio-ml:cpu-and-gpu-round-boundary
  - aio-ml:softmax
  - aio-ml:cross-entropy-loss
  - aio-ml:torch-optimizers
  - aio-ml:autograd-training
  - aio-ml:trained-mlp
  - aio-ml:k-means
  - aio-ml:lloyd-algorithm
  teaches:
  - gpu-colab-l4-workflow
  - open-ended-experiment-design
  - open-ended-model-evaluation
  - semi-supervised-pseudo-labeling
  - scientific-ml-inverse-problems
  - mixture-parameter-regression
  length: double
```
