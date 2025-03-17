# Preprocessing Pipeline Documentation
## Executive Summary

Quick Links: 
[Technical Documentation](technical_documentation.md) | [Theoretical Alignment](theoretical_alignment.md) | [Implementation Analysis](implementation_analysis.md)


### Overview
This documentation describes a preprocessing pipeline designed to transform online newspaper comments into context-rich datasets suitable for emotion analysis using Large Language Models (LLMs), aligned with Lisa Feldman Barrett's theory of constructed emotions.

### Key Components
1. **Technical Documentation**
   - Data transformation workflow (CSV → JSON → Markdown)
   - Context Sphere structure
   - Implementation considerations

2. **Theoretical Alignment**
   - Integration with Barrett's theory
   - Technical evolution enabling implementation
   - Context preservation approach

3. **Implementation Analysis**
   - Design decisions and rationale
   - Data quality considerations
   - Validation approach

### Quick Start
```mermaid
graph LR
    A[Raw Data] --> B[Preprocessing]
    B --> C[Context Sphere]
    C --> D[LLM Analysis]
```

### Detailed Pipeline Flow
```mermaid
graph TD
    subgraph Input
        A[Raw CSV Data] --> |Load| B[DataPreprocessor]
        B --> B1[Convert Dates]
        B --> B2[Handle Missing Values]
        B --> B3[Convert IDs]
        B --> B4[Create Features]
    end

    subgraph Intermediate
        B1 & B2 & B3 & B4 --> C[Preprocessed DataFrame]
        C --> |Serialize| D[Pickle Storage]
        D --> |Load| E[Thread Manager]
    end

    subgraph ThreadBuilding
        E --> E1[Build Comment Threads]
        E1 --> |Recursive Processing| E2[Hierarchical JSON]
        E2 --> F[JSON with Full Thread Structure]
    end

    subgraph ContextSphere
        F --> G[Context Sphere Builder]
        G --> G1[User Overview]
        G --> G2[Article Sections]
        G --> G3[Comment Threads]
        G1 & G2 & G3 --> H[Markdown Context Sphere]
    end

    subgraph Validation
        H --> I1[Automated Checks]
        H --> I2[Manual Verification]
        I1 --> |Token Count| J1[Token Validation]
        I1 --> |Structure| J2[Format Validation]
        I1 --> |Content| J3[Data Integrity]
        I2 --> |50-100 Samples| K[Quality Assurance]
    end

    subgraph Output
        J1 & J2 & J3 & K --> L[Validated Context Spheres]
        L --> M[LLM Pipeline Input]
    end

    %% Data Flow Annotations
    classDef process fill:#e1f5fe,stroke:#01579b
    classDef storage fill:#fff3e0,stroke:#ff6f00
    classDef validation fill:#f3e5f5,stroke:#7b1fa2
    classDef output fill:#e8f5e9,stroke:#2e7d32

    class A,B,B1,B2,B3,B4 process
    class C,D,E,F storage
    class G,G1,G2,G3,H process
    class I1,I2,J1,J2,J3,K validation
    class L,M output
```

### Key Features
- Context-rich data transformation
- Theory-aligned preprocessing
- Robust validation strategy

### Documentation Structure
- [Technical Documentation](technical_documentation.md)
- [Theoretical Alignment](theoretical_alignment.md)
- [Implementation Analysis](implementation_analysis.md)

### Important Considerations
- Token length: 5,000-15,000 tokens per context sphere
- UTF-8 encoding throughout
- Manual validation of 50-100 samples

### Future Work
- Scalability improvements
- Automated testing expansion
- Performance optimization
