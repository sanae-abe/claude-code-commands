---
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, TodoWrite, AskUserQuestion, Task
argument-hint: "[language-code] [--coverage|--consistency|--format|--cultural|--complete]"
description: Comprehensive internationalization (i18n) status check for any project
model: sonnet
---

# 🌍 i18n Completeness Check

Comprehensive internationalization (i18n) status check for any project.

Usage: `/i18n-check [language-code] [options]`

Examples:
- `/i18n-check` (Full completeness check for all languages)
- `/i18n-check --coverage` (Coverage-focused analysis)
- `/i18n-check ja --consistency` (Japanese terminology consistency check)
- `/i18n-check --cultural --detailed` (Detailed cultural adaptation review)

## Current i18n Project State

- Translation files: !`find . -name "*.json" -path "*/locales/*" -o -path "*/i18n/*" -o -path "*/lang/*" 2>/dev/null | wc -l || echo "0"` files found
- i18n Library: !`grep -E "i18next|vue-i18n|react-intl|gettext" package.json 2>/dev/null | head -1 || echo "Not detected"`
- Supported languages: !`ls -1 locales/ i18n/ lang/ 2>/dev/null || echo "No standard i18n directory"`
- Recent translations: !`git log --oneline --since="1 week ago" -- "**/locales/**" "**/i18n/**" | head -3 || echo "No recent updates"`
- Git status: !`git status --porcelain | grep -E "(locales|i18n|lang)" | wc -l || echo "0"` uncommitted translation changes

## Execution Flow

### 1. Initial Diagnosis and Check Strategy Decision
**TodoWrite required**:
1. Automatic analysis of i18n project structure
2. Translation file format and framework detection
3. Interactive check strategy selection
4. Incremental checking and result organization

### 2. Check Scope Determination
**Auto-determined from check target**:
- 🔥 **Urgent**: Pre-release completeness verification
- ⚡ **Important**: After new language addition or major updates
- 🎯 **Periodic**: Weekly/monthly maintenance
- 🔍 **Comprehensive**: All languages, all perspectives check

### 📊 Automated i18n Diagnosis

**Automated i18n project analysis:**
```bash
# i18n framework detection
echo "🌍 i18n Framework Detection:"
if [[ -f "package.json" ]]; then
    echo "React i18next:" && grep -c "react-i18next" package.json 2>/dev/null || echo "0"
    echo "Vue i18n:" && grep -c "vue-i18n" package.json 2>/dev/null || echo "0"
    echo "React Intl:" && grep -c "react-intl" package.json 2>/dev/null || echo "0"
    echo "i18next:" && grep -c "i18next" package.json 2>/dev/null || echo "0"
fi

# Translation file structure detection
echo "📁 Translation File Structure:"
find . -name "*.json" -path "*/locales/*" -o -path "*/i18n/*" -o -path "*/lang/*" 2>/dev/null | head -5 || echo "No translation files found"

# Supported languages detection
echo "🌐 Supported Languages:"
if [[ -d "locales" ]]; then
    ls -1 locales/
elif [[ -d "i18n" ]]; then
    ls -1 i18n/
elif [[ -d "public/locales" ]]; then
    ls -1 public/locales/
else
    echo "⚠️ No standard i18n directory structure detected"
fi

# Translation file format analysis
echo "📄 Translation File Formats:"
find . -name "*.json" -path "*i18n*" -o -path "*locale*" | wc -l | sed 's/^/JSON files: /'
find . -name "*.yaml" -path "*i18n*" -o -path "*locale*" | wc -l | sed 's/^/YAML files: /'
find . -name "*.po" -path "*i18n*" -o -path "*locale*" | wc -l | sed 's/^/PO files: /'

# Recent translation activity
echo "📊 Recent Translation Activity:"
git log --since="1 month ago" --name-only --pretty=format: | grep -E "(locales|i18n|lang)" | sort | uniq | wc -l | sed 's/^/Files modified: /'
```

## Interactive i18n Check Management (AskUserQuestion Integration)

### Primary Question: Check Scope Selection
```typescript
AskUserQuestion({
  questions: [{
    question: "Please select the scope and focus of the i18n check",
    header: "Check Scope",
    multiSelect: true,
    options: [
      {
        label: "completeness",
        description: "Translation completeness (missing key detection, coverage calculation)"
      },
      {
        label: "consistency",
        description: "Terminology consistency (unified translation of same concepts, inconsistency detection)"
      },
      {
        label: "format",
        description: "Technical quality (placeholder validation, encoding)"
      },
      {
        label: "cultural",
        description: "Cultural adaptation (language appropriateness, date/time formats, idioms)"
      },
      {
        label: "documentation",
        description: "Documentation translation (README, guides, examples)"
      },
      {
        label: "complete",
        description: "All-perspective comprehensive check (takes time)"
      }
    ]
  }]
})
```

### Secondary Question: Target Language Selection
```typescript
AskUserQuestion({
  questions: [{
    question: "Select languages to check (leave blank for all languages)",
    header: "Target Languages",
    multiSelect: true,
    options: [
      { label: "all", description: "All languages (all supported languages)" },
      { label: "en", description: "English" },
      { label: "ja", description: "Japanese (日本語)" },
      { label: "zh-CN", description: "Simplified Chinese (简体中文)" },
      { label: "zh-TW", description: "Traditional Chinese (繁體中文)" }
    ]
  }]
})
```

## Analysis Tasks

### 1. **Translation Completeness**
```bash
# Automated completeness check
echo "🔍 Translation Completeness Analysis:"

# Extract all keys from base language (usually English)
BASE_LANG_FILE="locales/en/common.json"  # Auto-detect
if [[ -f "$BASE_LANG_FILE" ]]; then
    BASE_KEYS=$(jq -r 'keys[]' "$BASE_LANG_FILE" 2>/dev/null | wc -l)
    echo "Base language keys: $BASE_KEYS"
else
    echo "⚠️ Base language file not found, scanning for reference..."
    BASE_LANG_FILE=$(find . -name "*.json" -path "*/locales/en/*" -o -path "*/i18n/en/*" | head -1)
fi

# Compare keys across all languages
for lang_file in locales/*/common.json i18n/*/common.json; do
    if [[ -f "$lang_file" ]]; then
        LANG_CODE=$(basename $(dirname "$lang_file"))
        LANG_KEYS=$(jq -r 'keys[]' "$lang_file" 2>/dev/null | wc -l)
        COVERAGE=$((LANG_KEYS * 100 / BASE_KEYS))
        echo "$LANG_CODE: $LANG_KEYS/$BASE_KEYS keys ($COVERAGE%)"
    fi
done
```

**Analysis items:**
- Extract all message keys from translation files
- Compare keys across all supported languages
- Report missing translations per language
- Calculate coverage percentage

### 2. **Terminology Consistency**
```bash
# Automated consistency check
echo "📝 Terminology Consistency Analysis:"

# Check for inconsistent translations
for term in "button" "error" "success" "cancel"; do
    echo "Term: $term"
    grep -r "\"$term\":" locales/ i18n/ 2>/dev/null | head -3
done

# Detect ambiguous translations
echo "⚠️ Ambiguous Translation Detection:"
# Find same key with different values across languages
# (requires custom script based on project structure)
```

**Analysis items:**
- Check for inconsistent translations of same concept
- Verify technical terms are translated consistently
- Flag ambiguous or conflicting translations

### 3. **Cultural Appropriateness**
```bash
# Cultural appropriateness check
echo "🌏 Cultural Appropriateness Analysis:"

# Date/time format check
grep -r "format.*date\|format.*time" locales/ i18n/ 2>/dev/null | head -3

# Number format check
grep -r "format.*number\|format.*currency" locales/ i18n/ 2>/dev/null | head -3

# Formal vs informal language detection
# (language-specific logic needed)
```

**Analysis items:**
- Review formal vs informal language choices
- Check idioms and metaphors are culturally adapted
- Verify date/time/number formats are locale-appropriate

### 4. **Technical Quality**
```bash
# Technical quality validation
echo "🔧 Technical Quality Validation:"

# Validate placeholder syntax
echo "Placeholder validation:"
grep -r "\{[0-9]\+\}\|%s\|%d\|{{.*}}" locales/ i18n/ 2>/dev/null | wc -l

# Check for hardcoded user-facing strings
echo "Hardcoded string detection:"
grep -r "console\.log\|alert\|confirm" src/ --include="*.ts" --include="*.tsx" | grep -v "i18n\|t(" | head -3

# Verify UTF-8 encoding
echo "Encoding validation:"
find locales/ i18n/ -name "*.json" -exec file {} \; | grep -v "UTF-8" || echo "✅ All files UTF-8"

# Test language switching functionality (manual test required)
echo "⚠️ Language switching test required (manual)"
```

**Analysis items:**
- Validate placeholder syntax ({0}, {1}, etc.) preserved
- Check for hardcoded user-facing strings
- Verify UTF-8 encoding throughout
- Test language switching functionality

### 5. **Documentation**
```bash
# Documentation translation check
echo "📚 Documentation Translation Analysis:"

# Check README files for all languages
for lang in en ja zh-CN zh-TW; do
    if [[ -f "README.$lang.md" || -f "docs/README.$lang.md" ]]; then
        echo "✅ README.$lang.md found"
    else
        echo "❌ README.$lang.md missing"
    fi
done

# Verify user guides
find docs/ -name "*.md" 2>/dev/null | grep -E "(en|ja|zh)" | head -5

# Validate code examples (language-neutral check)
grep -r "```" docs/ 2>/dev/null | wc -l | sed 's/^/Code examples: /'
```

**Analysis items:**
- Check README files for all languages
- Verify user guides are translated
- Validate code examples work for all locales

## Error Handling & Validation

### Pre-check Validation
```bash
# Check i18n project structure
if [[ ! -d "locales" && ! -d "i18n" && ! -d "lang" ]]; then
  echo "⚠️ No standard i18n directory detected"
  echo "Searching for translation files..."
  find . -name "*.json" | grep -E "(locale|i18n|lang|translation)" | head -5
fi

# Verify translation file format
for file in locales/**/*.json i18n/**/*.json; do
    if [[ -f "$file" ]]; then
        jq . "$file" >/dev/null 2>&1 || echo "❌ Invalid JSON: $file"
    fi
done

# Check git repository status
git status >/dev/null 2>&1 && echo "✅ Git repository detected" || echo "⚠️ Not a git repository"
```

### Common Issues & Solutions

#### Issue: "Translation files not found"
**Detection & Auto-resolution:**
```typescript
AskUserQuestion({
  questions: [{
    question: "Translation files not found. What would you like to do?",
    header: "File Detection",
    multiSelect: false,
    options: [
      { label: "auto-detect", description: "Auto-detect non-standard structure" },
      { label: "manual-specify", description: "Manually specify file paths" },
      { label: "create-structure", description: "Create standard i18n structure" },
      { label: "cancel", description: "Cancel check" }
    ]
  }]
})
```

#### Issue: "Invalid JSON format detected"
**Error recovery:**
```bash
# Automated JSON validation and repair suggestions
for file in locales/**/*.json i18n/**/*.json; do
    if ! jq . "$file" >/dev/null 2>&1; then
        echo "❌ Invalid JSON: $file"
        echo "Error details:"
        jq . "$file" 2>&1 | head -3
        echo "Suggested action: Review file syntax"
    fi
done
```

#### Issue: "Encoding errors detected"
**Encoding fix strategy:**
```bash
# Detect non-UTF-8 files
find locales/ i18n/ -name "*.json" -exec file {} \; | grep -v "UTF-8" > /tmp/encoding_issues.txt
if [[ -s /tmp/encoding_issues.txt ]]; then
    echo "⚠️ Non-UTF-8 files detected:"
    cat /tmp/encoding_issues.txt
    echo "Recommended: Convert to UTF-8 encoding"
fi
```

## Output Format

Generate a detailed report in this format:

```markdown
## i18n Status Report

### 📊 Supported Languages
- ✅ English (en) - 100% complete (450/450 keys)
- ✅ Japanese (ja) - 100% complete (450/450 keys)
- ⚠️ Chinese Simplified (zh-CN) - 98% complete (441/450 keys)
- ⚠️ Chinese Traditional (zh-TW) - 98% complete (441/450 keys)

### 📈 Translation Coverage
- **Total message keys**: 450
- **Fully translated languages**: 2/4
- **Missing translations**:
  - zh-CN: 9 keys (buttons.advanced, errors.network.*, help.faq.q3)
  - zh-TW: 9 keys (buttons.advanced, errors.network.*, help.faq.q3)

### 🔍 Terminology Consistency
- ✅ Technical terms: Consistent across all languages
- ⚠️ "button" translation: 3 different translations in ja (ボタン/釦/押しボタン)
- ⚠️ "error" translation: Inconsistent formality (エラー vs ご不便をおかけします)

### 🌏 Cultural Appropriateness
- ✅ Date formats: Properly localized (en: MM/DD/YYYY, ja: YYYY年MM月DD日)
- ✅ Number formats: Correct decimal/thousand separators
- ⚠️ Formal language: Mixed formal/informal in ja (needs unification)
- ❌ Idioms: English idiom "piece of cake" literally translated in zh-CN

### 🔧 Technical Quality
- ✅ Placeholder syntax: All {0}, {1} placeholders preserved
- ✅ Encoding: All files UTF-8
- ⚠️ Hardcoded strings: 12 instances found in src/components/
- ❌ Language switching: Not tested (manual testing required)

### 📚 Documentation
- ✅ README.en.md - Complete
- ✅ README.ja.md - Complete
- ⚠️ README.zh-CN.md - Outdated (last updated 3 months ago)
- ❌ README.zh-TW.md - Missing

### 🚨 Issues Found
1. **Missing translations (Priority: High)**
   - 9 keys missing in zh-CN and zh-TW
   - Files: locales/zh-CN/common.json, locales/zh-TW/common.json
   - Impact: Users will see English fallback

2. **Terminology inconsistency (Priority: Medium)**
   - "button" has 3 different translations in Japanese
   - Recommended: Use consistent "ボタン" across all instances

3. **Hardcoded strings (Priority: High)**
   - 12 user-facing strings not using i18n
   - Files: src/components/Header.tsx, src/pages/Dashboard.tsx
   - Impact: Cannot be translated

4. **Cultural adaptation issue (Priority: Low)**
   - English idioms literally translated
   - Files: locales/zh-CN/messages.json
   - Recommended: Use culturally appropriate equivalents

### ✅ Recommendations
1. **Immediate Actions**
   - Complete missing translations in zh-CN and zh-TW
   - Replace hardcoded strings with i18n keys
   - Standardize "button" translation in Japanese

2. **Short-term Improvements**
   - Update outdated README.zh-CN.md
   - Create README.zh-TW.md
   - Review and adapt culturally inappropriate translations

3. **Long-term Maintenance**
   - Implement automated i18n testing in CI/CD
   - Create terminology glossary for consistency
   - Regular i18n audits (monthly)
```

## Agent Execution Strategy

**Use the following agents in sequence:**

### Phase 1: Translation File Analysis
```bash
# Agent: code-reviewer
# Task: Analyze translation file structure and completeness
# Focus:
- Extract all translation files
- Parse JSON/YAML/PO formats
- Compare keys across languages
- Calculate coverage percentages
```

### Phase 2: Documentation Review
```bash
# Agent: documentation-engineer
# Task: Review translated documentation
# Focus:
- Check README files for all languages
- Verify user guide translations
- Validate code example compatibility
```

### Phase 3: Quality Analysis
```bash
# Agent: code-reviewer + security-auditor
# Task: Technical quality and security check
# Focus:
- Validate encoding (UTF-8)
- Check placeholder syntax
- Detect hardcoded strings
- Security: Verify no sensitive data in translation files
```

### Phase 4: Comprehensive Report
```bash
# Main agent: Consolidate all findings
# Task: Generate comprehensive status report
# Output:
- Structured markdown report
- Actionable recommendations
- Priority-ranked issues
```

## Command Integration

### Link with Other Commands
```bash
# After successful i18n check
echo "🚀 Next steps:"
echo "  /update-docs --i18n  # Update translation documentation"
echo "  /commit 'i18n: update translations for zh-CN, zh-TW'"
echo "  /mr 'i18n: complete missing translations and fix inconsistencies'"
```

### Quality Metrics Tracking
- **Translation coverage**: Percentage completion per language
- **Consistency score**: Terminology uniformity across languages
- **Technical quality**: Encoding, placeholder, hardcoded string checks
- **Documentation sync**: Translation documentation completeness

## Key Features Summary

### ✅ Implemented Core Features
- **Interactive guidance**: AskUserQuestion integration for scope selection
- **Automated detection**: i18n framework and file structure auto-detection
- **Multi-format support**: JSON/YAML/PO file analysis
- **Comprehensive analysis**: Completeness, consistency, cultural, technical, documentation
- **Error handling**: Robust validation and recovery strategies
- **Repository awareness**: Real-time git status and change tracking

### 🎯 Main Benefits
- **Quality**: Ensures high-quality translations across all languages
- **Consistency**: Enforces terminology standards
- **Completeness**: Identifies missing translations
- **Cultural awareness**: Validates cultural appropriateness
- **Efficiency**: Automated workflows reduce manual i18n tasks
- **Learning**: Guided process teaches i18n best practices

---

## Execution Start

**🎯 Goal**: Achieve automated system for comprehensive analysis of all project i18n status, efficiently checking translation quality, completeness, and cultural adaptation

Arguments: "{{args:arguments}}"

Parse arguments to identify check scope and target languages, auto-detect project i18n structure.

## 🚀 i18n Check Execution

Analyze current project i18n structure and launch appropriate specialized agents for comprehensive i18n check.
