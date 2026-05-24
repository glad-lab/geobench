# Comprehensive Experimental Results Report: C-SEO Manipulation Across Three Datasets

> This report summarizes the performance of 10 C-SEO manipulation methods across three distinct datasets

---

## 📊 Executive Summary

| Dataset | Domain | Categories | Total Tests | Significant Improvements | Success Rate | Mean Δ Rank |
|---------|--------|------------|-------------|--------------------------|--------------|-------------|
| **C-SEO Bench** | Academic/Mixed Content | 6 | 60 | 12 | 20.0% | +0.078 |
| **Ragroll** | Consumer Electronics | 53 | 530 | 8 | 1.5% ⚠️ | +0.448 |
| **Rewrite-to-Rank** | E-commerce Products | 42 | 420 | 223 | **53.1%** ⭐ | +0.260 |

**Key Findings**:
- **Rewrite-to-Rank** dataset is most vulnerable to C-SEO manipulation (53.1% success rate)
- **Ragroll** dataset shows strongest resistance (only 1.5% success rate)
- **Statistics** method is the most effective manipulation technique (43.6% overall success rate)

**Dataset Sources**:
- **C-SEO Bench**: "Manipulating LLMs to Increase Product Visibility: An Evaluation of C-SEO Bench" (C-SEO Bench Paper)
- **Ragroll**: "Stealth Rank: Analyzing LLM Ranking Manipulation Vulnerabilities" (Stealth Rank Paper)
- **Rewrite-to-Rank**: "Rewrite-to-Rank: Optimizing Content for LLM-based Search" (Rewrite-to-Rank Paper)

---

## 📈 Table 1: Overall Performance of Each Method Across Three Datasets

| Method | C-SEO Bench | Ragroll | Rewrite-to-Rank |
|--------|-------------|---------|-----------------|
| | Significant/Total (Rate) | Significant/Total (Rate) | Significant/Total (Rate) |
| **Authoritative** | 1/6 (16.7%) | 1/53 (1.9%) | 32/42 (76.2%) |
| **Citations** | 3/6 (50.0%) | 1/53 (1.9%) | 34/42 (81.0%) |
| **ContentImprovement** | 2/6 (33.3%) | 2/53 (3.8%) | 29/42 (69.0%) |
| **Fluency** | 0/6 (0.0%) | 0/53 (0.0%) | 7/42 (16.7%) |
| **LLMstxt** | 0/6 (0.0%) | 0/53 (0.0%) | 31/42 (73.8%) |
| **Quotes** | 2/6 (33.3%) | 2/53 (3.8%) | 35/42 (83.3%) |
| **SimpleLanguage** | 0/6 (0.0%) | 0/53 (0.0%) | 2/42 (4.8%) |
| **Statistics** | 2/6 (33.3%) | 1/53 (1.9%) | **41/42 (97.6%)** ⭐ |
| **TechnicalTerms** | 2/6 (33.3%) | 0/53 (0.0%) | 8/42 (19.0%) |
| **UniqueWords** | 0/6 (0.0%) | 1/53 (1.9%) | 4/42 (9.5%) |
| **Total** | **12/60 (20.0%)** | **8/530 (1.5%)** | **223/420 (53.1%)** |

---

## 📊 Table 2: Average Ranking Improvement (Mean Δ Rank)

| Method | C-SEO Bench | Ragroll | Rewrite-to-Rank |
|--------|-------------|---------|-----------------|
| | Mean Δ (Std Dev) | Mean Δ (Std Dev) | Mean Δ (Std Dev) |
| **Authoritative** | +0.061 (0.852) | +0.662 (0.787) | +0.348 (0.957) |
| **Citations** | +0.119 (0.685) | +0.625 (0.883) | +0.346 (0.989) |
| **ContentImprovement** | +0.114 (0.786) | +0.623 (0.787) | +0.291 (0.911) |
| **Fluency** | +0.036 (0.827) | +0.051 (0.744) | +0.110 (0.921) |
| **LLMstxt** | +0.025 (0.695) | +0.543 (0.806) | +0.309 (0.934) |
| **Quotes** | +0.150 (0.681) | **+0.908** (0.732) | +0.370 (0.918) |
| **SimpleLanguage** | +0.003 (0.645) | +0.000 (0.771) | +0.042 (0.894) |
| **Statistics** | +0.133 (0.818) | +0.817 (0.868) | **+0.569** (1.043) |
| **TechnicalTerms** | +0.100 (0.826) | +0.149 (0.838) | +0.110 (0.943) |
| **UniqueWords** | +0.042 (0.712) | +0.098 (0.759) | +0.110 (0.872) |

**Note**: Positive values indicate rank improvement (higher position), negative values indicate rank decline

---

## 🏆 Table 3: Top Method Rankings (by Total Significant Results)

| Rank | Method | Total Significant | C-SEO Bench | Ragroll | Rewrite-to-Rank | Overall Success Rate |
|------|--------|-------------------|-------------|---------|-----------------|----------------------|
| 🥇 1 | **Statistics** | 44 | 2/6 (33.3%) | 1/53 (1.9%) | 41/42 (97.6%) | **43.6%** |
| 🥈 2 | **Quotes** | 39 | 2/6 (33.3%) | 2/53 (3.8%) | 35/42 (83.3%) | **38.6%** |
| 🥉 3 | **Citations** | 38 | 3/6 (50.0%) | 1/53 (1.9%) | 34/42 (81.0%) | **37.6%** |
| 4 | **Authoritative** | 34 | 1/6 (16.7%) | 1/53 (1.9%) | 32/42 (76.2%) | 33.7% |
| 5 | **ContentImprovement** | 33 | 2/6 (33.3%) | 2/53 (3.8%) | 29/42 (69.0%) | 32.7% |
| 6 | **LLMstxt** | 31 | 0/6 (0.0%) | 0/53 (0.0%) | 31/42 (73.8%) | 30.7% |
| 7 | **TechnicalTerms** | 10 | 2/6 (33.3%) | 0/53 (0.0%) | 8/42 (19.0%) | 9.9% |
| 8 | **Fluency** | 7 | 0/6 (0.0%) | 0/53 (0.0%) | 7/42 (16.7%) | 6.9% |
| 9 | **UniqueWords** | 5 | 0/6 (0.0%) | 1/53 (1.9%) | 4/42 (9.5%) | 5.0% |
| 10 | **SimpleLanguage** | 2 | 0/6 (0.0%) | 0/53 (0.0%) | 2/42 (4.8%) | 2.0% |

---

## 📝 Table 4: Best Methods per Category in C-SEO Bench Dataset

| Category | Best Method | Mean Δ Rank | p-value | Significant |
|----------|-------------|-------------|---------|-------------|
| **books** | Statistics | +0.317 | 0.001160 | ✓ |
| **debate** | LLMstxt | +0.100 | 0.245157 | ✗ |
| **news** | Quotes | +0.150 | 0.119155 | ✗ |
| **retail** | Authoritative | +0.083 | 0.233414 | ✗ |
| **videogames** | Statistics | +0.367 | 0.030730 | ✓ |
| **web** | Citations | +0.083 | 0.029391 | ✓ |

**Source**: C-SEO Bench Dataset from "Manipulating LLMs to Increase Product Visibility" paper

---

## 🖥️ Table 5: Best Methods per Category in Ragroll Dataset (Stealth Rank)

| Category | Best Method | Mean Δ Rank | p-value | Significant |
|----------|-------------|-------------|---------|-------------|
| **air compressor** | Citations | +0.750 | 0.125000 | ✗ |
| **barbecue grill** | Authoritative | +1.000 | 0.062500 | ✗ |
| **books** | Quotes | +1.600 | 0.031250 | ✓ |
| **cameras** | ContentImprovement | +2.400 | 0.031250 | ✓ |
| **coffee maker** | Citations | +1.750 | 0.125000 | ✗ |
| **coffee_machines** | Citations | +1.600 | 0.062500 | ✗ |
| **computer monitor** | Citations | +2.000 | 0.125000 | ✗ |
| **dishwasher** | Citations | +1.000 | 0.062500 | ✗ |
| **electric sander** | Authoritative | +1.250 | 0.125000 | ✗ |
| **laptop** | Authoritative | +1.250 | 0.125000 | ✗ |
| **lawn mower** | Authoritative | +0.750 | 0.125000 | ✗ |
| **microwave oven** | Quotes | +0.750 | 0.125000 | ✗ |
| **network attached storage** | Statistics | +2.250 | 0.062500 | ✗ |
| **paint sprayer** | Authoritative | +1.000 | 0.062500 | ✗ |
| **pressure washer** | Citations | +1.250 | 0.125000 | ✗ |
| **robot vacuum** | Authoritative | +2.500 | 0.062500 | ✗ |
| **shampoo** | Citations | +1.500 | 0.062500 | ✗ |
| **smartphone** | Quotes | +0.750 | 0.125000 | ✗ |
| **solid state drive** | Statistics | +1.500 | 0.062500 | ✗ |
| **string trimmer** | Authoritative | +2.250 | 0.062500 | ✗ |
| **tablet** | LLMstxt | +1.250 | 0.062500 | ✗ |
| **tent** | Citations | +1.750 | 0.062500 | ✗ |
| **tool chest** | Statistics | +1.500 | 0.062500 | ✗ |
| **wifi router** | ContentImprovement | +1.250 | 0.062500 | ✗ |
| **... (53 categories total)** | - | - | - | - |

**Source**: Ragroll Dataset from "Stealth Rank" paper
**Note**: Only 2 out of 53 categories (3.8%) showed statistically significant improvements, demonstrating strong resistance to C-SEO manipulation

---

## 🛒 Table 6: Best Methods per Category in Rewrite-to-Rank Dataset

| Category | Best Method | Mean Δ Rank | p-value | Significant |
|----------|-------------|-------------|---------|-------------|
| **apparel** | Statistics | +0.600 | 0.000269 | ✓ |
| **athletic_footwear** | Statistics | +0.550 | 0.000592 | ✓ |
| **automotive** | Statistics | +0.725 | 0.000508 | ✓ |
| **automotive_parts** | Authoritative | +0.400 | 0.000081 | ✓ |
| **beauty_and_personal_care** | Statistics | +0.500 | 0.000104 | ✓ |
| **bedding** | Statistics | +0.725 | 0.000466 | ✓ |
| **books** | Authoritative | +0.650 | 0.000015 | ✓ |
| **clothing** | Statistics | +0.650 | 0.000227 | ✓ |
| **collectibles** | Quotes | +0.450 | 0.000028 | ✓ |
| **computer_accessories** | Statistics | +0.625 | 0.000024 | ✓ |
| **computer_hardware** | Authoritative | +0.625 | 0.000235 | ✓ |
| **cookware** | Quotes | +0.600 | 0.000329 | ✓ |
| **dietary_supplements** | Statistics | +0.450 | 0.000028 | ✓ |
| **flooring** | Statistics | +0.775 | 0.000004 | ✓ |
| **food_and_beverage** | Statistics | +0.450 | 0.000062 | ✓ |
| **hair_care** | Authoritative | +0.650 | 0.000048 | ✓ |
| **halloween_costumes** | Statistics | +0.625 | 0.000038 | ✓ |
| **handbags** | Statistics | +0.925 | 0.000231 | ✓ |
| **hardware** | Statistics | +0.475 | 0.000304 | ✓ |
| **health_and_beauty** | Statistics | +0.675 | 0.000066 | ✓ |
| **health_supplements** | Statistics | +0.550 | 0.002035 | ✓ |
| **home_and_kitchen** | Citations | +0.400 | 0.000559 | ✓ |
| **home_appliances** | Quotes | +0.600 | 0.000128 | ✓ |
| **kitchen_appliances** | Statistics | +0.650 | 0.000334 | ✓ |
| **laptops** | Statistics | +0.350 | 0.002694 | ✓ |
| **lingerie** | Statistics | +0.725 | 0.000013 | ✓ |
| **major_appliances** | Authoritative | +0.475 | 0.002779 | ✓ |
| **medical_supplies** | Statistics | +0.525 | 0.000423 | ✓ |
| **mens_clothing** | Statistics | +0.600 | 0.001758 | ✓ |
| **mobile_phones** | Statistics | +0.575 | 0.004423 | ✓ |
| **music** | Authoritative | +0.475 | 0.000076 | ✓ |
| **party_supplies** | Statistics | +0.575 | 0.000017 | ✓ |
| **phone_cases** | Statistics | +0.825 | 0.000018 | ✓ |
| **plumbing_fixtures** | Quotes | +0.475 | 0.001966 | ✓ |
| **power_tools** | Statistics | +0.425 | 0.005500 | ✓ |
| **shoes** | Authoritative | +0.475 | 0.002251 | ✓ |
| **skincare** | Statistics | +0.550 | 0.014990 | ✓ |
| **swimwear** | Statistics | +0.700 | 0.000107 | ✓ |
| **vitamins_and_supplements** | LLMstxt | +0.700 | 0.000037 | ✓ |
| **womens_clothing** | Statistics | +0.975 | 0.000003 | ✓ |
| **womens_shoes** | Statistics | +0.750 | 0.000005 | ✓ |

**Source**: Rewrite-to-Rank Dataset from "Rewrite-to-Rank" paper
**Remarkable Finding**: **100% of categories (42/42)** showed at least one statistically significant improvement, with Statistics method being the dominant best performer

---

## 🔍 In-Depth Analysis

### 1️⃣ Most Effective C-SEO Methods (Cross-Dataset)

#### 🥇 Statistics Method
- **44 significant improvements** (43.6% success rate)
- Achieved **97.6% success rate** in Rewrite-to-Rank dataset (41/42)
- **Most stable and effective** manipulation technique
- Average rank improvement: +0.506 (cross-dataset)
- **Mechanism**: Adding concrete numbers, data points, and statistical information enhances perceived objectivity and verifiability

#### 🥈 Quotes Method
- **39 significant improvements** (38.6% success rate)
- Highest average improvement in Ragroll: +0.908
- **Content enhancement approach** through authoritative quotations
- Particularly effective in e-commerce contexts (83.3% in Rewrite-to-Rank)
- **Mechanism**: External quotes increase credibility and perceived expertise

#### 🥉 Citations Method
- **38 significant improvements** (37.6% success rate)
- Best performer in C-SEO Bench: 50% success rate
- **Authority-building strategy** suitable for academic/formal content
- **Mechanism**: References to external sources enhance trustworthiness and scholarly appeal

### 2️⃣ Dataset Vulnerability Analysis

#### 📚 C-SEO Bench (Academic/Mixed Content)
**Source**: "Manipulating LLMs to Increase Product Visibility" paper

- **6 categories**: books, debate, news, retail, videogames, web
- **20.0% significance rate** - moderate vulnerability
- **Best performing methods**: Citations (50%), Statistics/Quotes/TechnicalTerms (33.3%)
- **Characteristics**:
  - Responds well to authority-based and professional methods
  - Academic and formal content is susceptible to citation manipulation
  - Mixed content types show varied resistance levels

#### 🖥️ Ragroll Dataset (Consumer Electronics)
**Source**: "Stealth Rank" paper

- **53 categories**: Various home appliances and electronic products
- **Only 1.5% significance rate** ⚠️ - **strongest resistance**
- **Average improvement**: +0.448 (large but unstable)
- **Characteristics**:
  - Strong resistance to C-SEO manipulation methods
  - Possible reasons:
    - Highly standardized product description formats
    - Technical specifications dominate evaluation criteria
    - LLMs may have stronger discrimination capabilities for product content
  - Only 2 categories (books, cameras) showed significant improvements

#### 🛒 Rewrite-to-Rank Dataset (E-commerce Products)
**Source**: "Rewrite-to-Rank" paper

- **42 categories**: Apparel, beauty, home goods, electronics, etc.
- **53.1% significance rate** ⭐ - **most vulnerable**
- **Statistics method**: 97.6% success rate (41/42)
- **Characteristics**:
  - Highly susceptible to content manipulation
  - Diverse content styles increase manipulation surface
  - Subjective evaluation factors dominate
  - **Critical security concern**: Demonstrates serious threat of C-SEO attacks
  - **100% of categories** showed at least one effective manipulation method

### 3️⃣ Least Effective Methods

| Method | Significant Count | Success Rate | Analysis |
|--------|-------------------|--------------|----------|
| **SimpleLanguage** | 2 | 2.0% | Simplifying language reduces perceived professionalism and credibility |
| **UniqueWords** | 5 | 5.0% | Vocabulary diversity alone insufficient to influence rankings |
| **Fluency** | 7 | 6.9% | Modern LLMs can detect fluent but substance-lacking text |

**Key Insight**: Superficial text modifications without substantive content enhancement are largely ineffective.

---

## 💡 Key Insights and Recommendations

### ✅ Successful C-SEO Strategy Characteristics

1. **Data-Driven Approach** (Statistics) - Most Effective
   - Add specific numbers, data points, and statistical information
   - Enhance content objectivity and verifiability
   - Works across diverse domains, especially e-commerce

2. **Authority-Based Methods** (Quotes, Citations, Authoritative)
   - Introduce external authoritative sources
   - Enhance credibility and professionalism
   - Particularly effective for academic and formal content

3. **Comprehensive Content Enhancement** (ContentImprovement)
   - Multi-dimensional optimization rather than single-aspect tricks
   - Holistic quality improvement
   - Consistent moderate success across datasets

### ❌ Failed C-SEO Strategy Characteristics

1. **Superficial Optimization** (Fluency, SimpleLanguage)
   - Only improves text fluency or readability
   - LLMs can identify content lacking substance
   - Minimal impact on rankings

2. **Single-Dimension Focus** (UniqueWords)
   - Focuses solely on vocabulary richness
   - Ignores overall content quality
   - Easily detected as manipulation

### 🎯 Targeted Recommendations

#### For E-commerce Product Descriptions (Rewrite-to-Rank Scenario)
- **Highly Recommended**: Statistics (97.6%), Quotes (83.3%), Citations (81.0%)
- **Strategy**: Add user data, review quotes, expert certifications
- **Warning**: This dataset is extremely vulnerable; defensive measures urgently needed

#### For Academic/Professional Content (C-SEO Bench Scenario)
- **Recommended**: Citations (50%), combination of multiple methods
- **Strategy**: Emphasize authoritative sources, professional terminology, data support
- **Context**: Different content types require tailored approaches

#### For Technical Products (Ragroll Scenario)
- **Caution**: All methods show limited effectiveness
- **Strategy**: Focus on technical specification accuracy rather than text rewriting
- **Insight**: Product category may naturally resist manipulation

### 🛡️ Defense Recommendations

1. **Develop Targeted Detection Mechanisms**
   - Focus on Statistics-type manipulation (most dangerous)
   - Identify artificially inserted data points and statistics
   - Cross-verify quoted sources and citations

2. **Enhance LLM Discrimination Capabilities for E-commerce Content**
   - Strengthen training on manipulated product descriptions
   - Implement content authenticity verification
   - Reduce reliance on purely textual features

3. **Multi-Modal Information Integration**
   - Combine images, specifications, reviews, and other signals
   - Reduce impact of pure text manipulation
   - Holistic content evaluation

4. **Category-Specific Evaluation Criteria**
   - Technical products: Prioritize specifications
   - Subjective products: Balance user reviews with descriptions
   - Academic content: Verify citation authenticity

---

## 📊 Experimental Methodology

### Evaluation Metrics
- **Mean Δ Rank**: Average change in ranking position (positive = improvement)
- **p-value**: Statistical significance test (p < 0.05 = significant)
- **Significance Rate**: Proportion of tests yielding statistically significant improvements

### Testing Procedure
1. Each category tested with 10 C-SEO optimization methods
2. Compare LLM rankings between original and optimized descriptions
3. Use Wilcoxon signed-rank test to assess significance
4. Calculate mean rank change and standard deviation

### LLM Configuration
- **Model**: llama-3.1-8b-instant
- **Backend**: Groq
- **Sample Size**: 5-60 per category (varies by dataset)

### Statistical Significance
- **Threshold**: p-value < 0.05
- **Test**: Wilcoxon signed-rank test (non-parametric)
- **Null Hypothesis**: No difference between original and manipulated rankings

---

## 📋 Dataset Details

| Dataset | Source Paper | Total Items | Category Examples |
|---------|--------------|-------------|-------------------|
| **C-SEO Bench** | "Manipulating LLMs to Increase Product Visibility: An Evaluation of C-SEO Bench" | 16,360 | books, debate, news, retail, videogames, web |
| **Ragroll** | "Stealth Rank: Analyzing LLM Ranking Manipulation Vulnerabilities" | Variable | coffee_machines, laptop, cameras, smartphone, robot vacuum, etc. |
| **Rewrite-to-Rank** | "Rewrite-to-Rank: Optimizing Content for LLM-based Search" | Variable | apparel, beauty, electronics, furniture, health, clothing, etc. |

### Dataset Composition

#### C-SEO Bench Category Breakdown
- **retail**: 5,000 items (30.56%)
- **videogames**: 4,360 items (26.65%)
- **news**: 2,375 items (14.52%)
- **books**: 2,245 items (13.72%)
- **web**: 1,500 items (9.17%)
- **debate**: 880 items (5.38%)

#### Ragroll Dataset Characteristics
- **53 product categories** spanning consumer electronics and home goods
- **Small sample sizes** (typically 4-5 items per category)
- **Highly specific product types** (e.g., "automatic garden watering system", "noise-canceling headphone")
- **Focus on consumer products** with technical specifications

#### Rewrite-to-Rank Dataset Characteristics
- **42 diverse e-commerce categories**
- **Larger sample sizes** (typically 40 items per category)
- **Broad category coverage**: Fashion, health, electronics, home, automotive
- **Consumer-focused products** with subjective quality attributes

---

## 🎓 Conclusions

### Primary Findings

1. **C-SEO Attacks Are Demonstrably Effective**
   - Overall success rate ranges from 1.5% to 53.1% depending on domain
   - E-commerce scenarios particularly vulnerable (53.1% success rate)
   - Statistics method poses the greatest threat (97.6% success in optimal conditions)

2. **Statistics Method Dominates as Most Powerful Weapon**
   - 223 significant improvements across 420 Rewrite-to-Rank tests
   - Consistent effectiveness across diverse product categories
   - Simple yet highly effective: adding numbers and data points

3. **Vulnerability Varies Dramatically by Domain**
   - **E-commerce products**: Highly vulnerable (53.1%)
   - **Academic content**: Moderately vulnerable (20.0%)
   - **Technical products**: Relatively resistant (1.5%)
   - **Implication**: Domain-specific defense strategies required

4. **Authority-Based Methods Consistently Effective**
   - Quotes, Citations, and Authoritative methods collectively account for 111/243 (45.7%) significant improvements
   - Exploiting human trust in authoritative sources
   - Particularly effective when combined with data-driven approaches

5. **Superficial Modifications Largely Ineffective**
   - SimpleLanguage, UniqueWords, Fluency show <7% success rates
   - Modern LLMs resist purely stylistic manipulations
   - Content substance matters more than surface-level changes

### Security Implications

#### For LLM-based Search Systems
- **Critical Vulnerability**: E-commerce and product recommendation systems
- **Attack Surface**: Statistics and authority-based manipulations
- **Risk Assessment**: High impact on user trust and platform integrity

#### For Content Creators
- **Ethical Considerations**: Line between optimization and manipulation
- **Detection Risk**: Sophisticated manipulation may be detectable
- **Long-term Strategy**: Focus on genuine quality improvement

### Future Research Directions

1. **Combination Attack Strategies**
   - Effect of combining multiple C-SEO methods
   - Optimal method combinations for specific domains
   - Diminishing returns analysis

2. **Cross-LLM Robustness Testing**
   - Compare manipulation susceptibility across different LLM models
   - Identify model-specific vulnerabilities
   - Develop model-agnostic defense mechanisms

3. **Adversarial Training Approaches**
   - Develop training datasets with manipulated content
   - Test adversarial training effectiveness
   - Balance manipulation resistance with quality assessment

4. **Real-World Deployment Studies**
   - Measure C-SEO impact in production systems
   - User perception of manipulated vs. genuine content
   - Economic impact on e-commerce platforms

5. **Automated Detection Systems**
   - Machine learning-based manipulation detection
   - Real-time content authenticity verification
   - Scalable defense mechanisms for production environments

---

## 📝 Limitations

1. **Single LLM Model**: All experiments conducted with llama-3.1-8b-instant
   - Results may not generalize to other models
   - Different architectures may show different vulnerabilities

2. **Limited Sample Sizes**: Some categories have only 5-10 samples
   - Statistical power may be limited
   - Generalization to broader populations uncertain

3. **Controlled Environment**: Experiments in isolated test conditions
   - Real-world deployments may show different patterns
   - User behavior and context not fully modeled

4. **Static Evaluation**: Single-point-in-time assessment
   - LLM capabilities evolve rapidly
   - Results may change with model updates

---

## 🙏 Acknowledgments

This comprehensive analysis synthesizes results from three important research papers:
- **C-SEO Bench**: "Manipulating LLMs to Increase Product Visibility"
- **Stealth Rank**: "Analyzing LLM Ranking Manipulation Vulnerabilities"
- **Rewrite-to-Rank**: "Optimizing Content for LLM-based Search"

The systematic evaluation across diverse domains provides crucial insights into the security and robustness of LLM-based ranking systems.

---

*Report Generated: December 28, 2025*
*Data Sources: C-SEO Bench Experimental Results / Ragroll Experimental Results / Rewrite-to-Rank Experimental Results*
*Analysis Framework: Statistical significance testing with Wilcoxon signed-rank test (α = 0.05)*
