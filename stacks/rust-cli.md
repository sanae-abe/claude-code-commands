# Rust CLI Development - AI Reference

> **AI Usage Note**: Sections marked `[CRITICAL]` are required for every CLI task. `[REFERENCE]` sections are optional lookup tables.

---

## [CRITICAL] Quick Start Commands

```bash
# Development (99% usage)
cargo build              # Debug build
cargo run                # Build + run
cargo test               # Run tests
cargo clippy             # Linter (recommended)

# Release build (90% usage)
cargo build --release    # Optimized build
cargo run --release      # Release mode

# Code quality (85% usage)
cargo fmt                # Format code
cargo clippy --all-targets --all-features  # Strict lint
cargo doc --open         # Generate + view docs
```

---

## [CRITICAL] Quality Standards

### Code Quality
- **clippy 0 warnings**: `cargo clippy` must pass with no warnings
- **rustfmt unified**: `cargo fmt` for automatic formatting
- **unwrap() prohibited**: Use `?` operator or `expect()` with explanation

### Type Safety
- **Option/Result usage**: Null safety, error handling
- **Ownership system**: Leverage borrow checker, compile-time safety
- **Lifetimes**: Proper lifetime annotations

### Testing
- **Unit tests**: `#[test]`, `#[cfg(test)]` modules
- **Integration tests**: `tests/` directory
- **Coverage**: 80%+ target

---

## [CRITICAL] Development Workflow & Quality Checks

### Post-Edit Mandatory Checks

**Recommended execution order**:
```bash
# 1. Format (code style unification)
cargo fmt

# 2. Static analysis (0 warnings across all features)
cargo clippy --all-features -- -D warnings

# 3. Compile check (type error detection)
cargo check --all-features

# 4. Unit tests (regression prevention)
cargo test --lib

# 5. (Optional) Integration tests
cargo test --test '*'

# 6. (Optional) Full tests + coverage
cargo tarpaulin --all-features --workspace --timeout 300
```

**Time-constrained cases (priority order)**:
```bash
# Minimum (within 30s): fmt + clippy only
cargo fmt && cargo clippy --all-features -- -D warnings

# Standard (within 2min): fmt + clippy + unit tests
cargo fmt && cargo clippy --all-features -- -D warnings && cargo test --lib

# Complete (within 10min): above + all tests
cargo fmt && cargo clippy --all-features -- -D warnings && cargo test
```

**Exception cases**:
- **Large refactoring**: fmt/clippy only, tests at final stage
- **Prototype implementation**: clippy warnings deferred (must resolve before finalization)
- **Emergency fix**: minimum tests, full tests later

**Automation (recommended)**:
```bash
# Set as Git pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
set -e
cargo fmt --check || { echo "Run: cargo fmt"; exit 1; }
cargo clippy --all-features -- -D warnings
cargo test --lib
EOF
chmod +x .git/hooks/pre-commit
```

---

## [CRITICAL] Error Handling Rules

### Prohibited
- ❌ `unwrap()` / `expect()` in production code (panic risk)
- ❌ Panic in library code (no choice for caller)
- ❌ Silencing errors (`let _ = result;`)

### Recommended
- ✅ `?` operator for error propagation
- ✅ `Result<T, E>` return
- ✅ Error types: `thiserror` (library), `anyhow` (application)
- ✅ Detailed info via custom error types

### Exceptionally allowed
- ✅ `unwrap()` in test code
- ✅ `expect("reason")` for invariants (e.g., guaranteed initialized)
- ✅ `.expect()` in `main()` (startup failure)

**Examples**:
```rust
// ❌ Bad: panic risk
let config = std::fs::read_to_string("config.toml").unwrap();

// ✅ Good: error propagation
let config = std::fs::read_to_string("config.toml")?;

// ✅ Good: clear reason
let config = std::fs::read_to_string("config.toml")
    .expect("config.toml must exist in binary directory");
```

---

## [CRITICAL] Security Standards & Automation

### Security Check Automation

**Prohibited pattern detection (Claude Code execution recommended)**:
```bash
# Detect unwrap() (exclude test code)
rg "\.unwrap\(\)" --type rust --glob '!**/tests/**' --glob '!**/*_test.rs'

# Detect unsafe
rg "unsafe\s+\{" --type rust

# Detect eval-like patterns
rg "std::process::Command::new.*format!" --type rust
```

**Response when detected**:
- `unwrap()` → Replace with `?` operator or `expect("reason")`
- `unsafe` → Consider alternatives or add detailed SAFETY comment
- Command injection risk → Use argument arrays, not string interpolation

### Dependency Security

**Manual checks**:
```bash
# Security audit
cargo audit              # Security audit

# Dependency updates
cargo update             # Update Cargo.lock
cargo outdated           # Check outdated dependencies
```

**CI/CD integration**:
```bash
# .github/workflows/security.yml recommended
- run: cargo audit --deny warnings
- run: cargo deny check advisories
```

### Memory Safety
- **Ownership**: Compile-time memory safety guarantee
- **Borrow checker**: Data race prevention
- **unsafe minimization**: Minimal unsafe, thorough review

---

## [CRITICAL] unsafe Code Rules

> **Note**: Usually unnecessary for CLI development. Refer only when needed for systems programming

- **Prohibited in principle**: Use only when truly necessary
- **Mandatory documentation**: Detailed safety contract description
  ```rust
  // SAFETY: ptr always points to valid memory,
  // guaranteed not to be freed by reference count management
  unsafe { *ptr }
  ```
- **Review required**: Multiple person review for unsafe blocks
- **Consider alternatives**: Always consider safe abstraction possibilities

---

## [REFERENCE] Dependency Management

- **When editing Cargo.toml**: `cargo update` to check dependency impact
- **When adding dependencies**: `cargo audit` for security check (weekly recommended)
- **MSRV management**: Explicit `rust-version = "1.75"` in `Cargo.toml`
- **Feature flags**: Minimal defaults, explicitly enable optional features

---

## [REFERENCE] Testing & Quality Standards

- **Test coverage**: 60-80% target for new features (project dependent)
- **Doc tests**: Required for public APIs (`cargo test --doc`)
- **Benchmarks**: Use `criterion` for performance-critical features
- **Property-based testing**: Use `proptest` for boundary condition tests

---

## [REFERENCE] Common Patterns & Examples

### CLI Argument Parsing (clap)
```rust
use clap::Parser;

/// Simple file search tool
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Search pattern
    pattern: String,

    /// Search target file
    #[arg(short, long, default_value = ".")]
    path: String,

    /// Case insensitive
    #[arg(short, long)]
    ignore_case: bool,
}

fn main() {
    let args = Args::parse();
    println!("Searching for '{}' in {}", args.pattern, args.path);
    // ...
}

// Result: auto-generated help, type-safe argument parsing
// $ ./myapp --help for automatic usage display
```

### Error Handling Improvement (anyhow)
```rust
use anyhow::{Context, Result};

fn read_config() -> Result<Config> {
    let content = std::fs::read_to_string("config.toml")
        .context("Failed to read config.toml")?;

    let config: Config = toml::from_str(&content)
        .context("Failed to parse config.toml")?;

    Ok(config)
}

fn main() -> Result<()> {
    let config = read_config()?;
    // ...
    Ok(())
}

// Result: no panic, clear error messages
```

### Parallel Processing (rayon)
```rust
use rayon::prelude::*;

// ❌ Serial processing (slow)
fn process_items(items: &[Item]) -> Vec<Result> {
    items.iter().map(|item| process(item)).collect()
}
// Processing time: 10s

// ✅ Parallel processing (rayon)
fn process_items(items: &[Item]) -> Vec<Result> {
    items.par_iter().map(|item| process(item)).collect()
}
// Processing time: 2.5s (4x speedup on 4 cores)
```

---

## [REFERENCE] Recommended Crates

### By Category

**Error Handling**:
- `anyhow` - Simple error handling, context addition
- `thiserror` - Custom error type definition
- `Result<T>` - Error propagation (`?` operator)

**CLI Development**:
- `clap` - Argument parsing, auto help generation
- `colored` - Color output
- `indicatif` - Progress bars
- `env_logger`/`tracing` - Logging

**Performance**:
- `rayon` - Data parallelism
- `tokio` - Async I/O, async/await
- `criterion` - Benchmarking

**File Operations**:
- `walkdir` - Directory traversal
- `glob` - File pattern matching
- `tempfile` - Temporary files

**Concurrency**:
- `rayon` - Data parallelism
- `tokio` - Async runtime
- `crossbeam` - Concurrency utilities

---

## [REFERENCE] Performance Optimization

### Optimization Levels
```toml
# Cargo.toml
[profile.release]
opt-level = 3            # Maximum optimization
lto = true               # Link Time Optimization
codegen-units = 1        # Single code generation unit (optimization priority)
strip = true             # Strip debug symbols
```

### Benchmarking
```rust
// benches/my_benchmark.rs
use criterion::{criterion_group, criterion_main, Criterion};

fn fibonacci_benchmark(c: &mut Criterion) {
    c.bench_function("fib 20", |b| b.iter(|| fibonacci(20)));
}

criterion_group!(benches, fibonacci_benchmark);
criterion_main!(benches);
```

```bash
cargo bench              # Run benchmarks
```

---

## [REFERENCE] Cross-Compilation

```bash
# Add targets
rustup target add x86_64-pc-windows-gnu
rustup target add x86_64-apple-darwin
rustup target add x86_64-unknown-linux-gnu

# Build
cargo build --release --target x86_64-pc-windows-gnu
cargo build --release --target x86_64-apple-darwin
cargo build --release --target x86_64-unknown-linux-gnu

# Result: binaries for each platform generated
# Located in target/{target}/release/
```

---

## Version Management & Maintenance

### Auto-Update Triggers (AI Context)

**Update conditions**:

1. **Rust Edition Upgrade** (every 3 years): 2018 → 2021 → 2024
   - Review all code examples for new syntax
   - Update MSRV in document header

2. **Major Crate Updates** (yearly check):
   - `clap` 4.x → 5.x: Update argument parsing examples
   - `tokio` 1.x → 2.x: Review async patterns
   - `anyhow` 1.x → 2.x: Check API changes

3. **Security Advisory** (immediate):
   - Critical vulnerability in recommended crates
   - Update "Prohibited" section if new attack vector discovered

**Update verification**:
```bash
# Check if examples still compile
cd /tmp && cargo init --name test-project
# Copy examples from this doc → verify with cargo check
```

### Document Metadata

- **Primary Use Case**: CLI tool implementation requests (weekly)
- **Secondary Use Case**: Code review for Rust projects (monthly)
- **Auto-update Trigger**: Rust edition upgrade (yearly)
- **Obsolescence Risk**: Low (Rust stability policy)
- **Related Docs**: `~/.claude/stacks/shell-cli.md` (Shell vs Rust decision)
- **Target**: Claude Code AI assistant
- **Rust Version**: 1.75+ (MSRV)
- **Last Updated**: 2025-11-12
- **Optimization**: Reduced from 349 to 235 lines (33% reduction)

---

## Additional Resources

- **Rust Official**: https://www.rust-lang.org/
- **The Rust Programming Language**: https://doc.rust-lang.org/book/
- **Rust by Example**: https://doc.rust-lang.org/rust-by-example/
- **crates.io**: https://crates.io/
