# GitHub Issue Template: Evaluate Django-Compressor Alternatives

**Copy the content below to create a new GitHub issue**

---

## Title
`Evaluate and potentially migrate away from django-compressor dependency conflicts`

## Labels
- `enhancement`
- `dependencies`
- `frontend`
- `research`

## Issue Description

### Background

Following the resolution of issue #86 (rcssmin dependency conflict), we should evaluate long-term alternatives to `django-compressor` to avoid future dependency conflicts and potentially modernize our CSS/JS asset pipeline.

### Current Situation

- **Current Setup**: `django-compressor==4.5.1` + `rcssmin==1.1.2`
- **Issue**: Hard dependency pin prevents rcssmin upgrades
- **Temporary Solution**: Dependabot configured to ignore rcssmin updates
- **Documentation**: Comprehensive alternatives analysis in `docs/CSS_COMPRESSION_ALTERNATIVES.md`

### Proposed Investigation

Research and potentially implement one of the documented alternatives:

#### Option 1: Django-Pipeline Migration 🔄
- **Package**: `django-pipeline`
- **Effort**: Medium (template changes required)
- **Benefits**: More flexible CSS minifier backends, active maintenance
- **Timeline**: Next major frontend update

#### Option 2: Build-Time Minification 🛠️
- **Approach**: PostCSS + cssnano during build, serve with WhiteNoise
- **Effort**: High (build process changes)
- **Benefits**: Modern toolchain, no runtime dependencies, faster serving
- **Timeline**: During next DevOps/CI improvements

#### Option 3: Simple Filter Switch 🔧
- **Approach**: Keep django-compressor, disable CSS minification
- **Effort**: Low (settings change only)
- **Benefits**: Immediate dependency conflict resolution
- **Trade-off**: Slightly larger CSS files

#### Option 4: CDN-Based Minification ☁️
- **Approach**: CloudFlare or similar auto-minification
- **Effort**: Low (configuration only)
- **Benefits**: No server-side processing, global CDN benefits
- **Consideration**: External dependency, potential costs

### Tasks

- [ ] **Research Phase**
  - [ ] Review current CSS/JS asset usage patterns
  - [ ] Benchmark current compression ratios and performance
  - [ ] Evaluate team expertise for different approaches

- [ ] **Technical Evaluation**
  - [ ] Create proof-of-concept for top 2 alternatives
  - [ ] Performance comparison (build time, file sizes, page load)
  - [ ] Developer experience assessment

- [ ] **Implementation Planning**
  - [ ] Migration strategy and timeline
  - [ ] Risk assessment and rollback plan
  - [ ] Documentation and training requirements

- [ ] **Decision**
  - [ ] Present findings to team
  - [ ] Select preferred approach
  - [ ] Plan implementation or maintain current setup

### Acceptance Criteria

- [ ] Comprehensive evaluation of at least 2 alternatives completed
- [ ] Performance impact analysis documented
- [ ] Migration effort estimation provided
- [ ] Team consensus on approach (migrate vs. maintain)
- [ ] If migrating: implementation plan with timeline
- [ ] If maintaining: long-term monitoring strategy

### Priority

**Low-Medium** - This is not urgent since the current setup is stable and working. Can be scheduled for:
- Next planned frontend refactor
- DevOps improvements cycle
- When team has bandwidth for infrastructure improvements

### Related Documentation

- `docs/CSS_COMPRESSION_ALTERNATIVES.md` - Comprehensive alternatives analysis
- `docs/DEPENDENCY_NOTES.md` - Current dependency resolution notes
- `.github/dependabot.yml` - Dependabot configuration with rcssmin ignore

### Dependencies

- Completion of any major frontend changes
- Available development bandwidth
- Potential coordination with DevOps for build process changes

---

**Note**: This issue serves as a tracking mechanism for potential future improvements. The current setup with dependency ignore is stable and production-ready.