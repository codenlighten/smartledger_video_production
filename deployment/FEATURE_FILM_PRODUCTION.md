# 90-Minute Feature Film Production with HunyuanVideo

## Project Specifications

**Target:** 90-minute movie from 8-second clips
- Total runtime: 90 minutes = 5,400 seconds
- Clip length: 8 seconds each
- **Clips needed:** 5,400 ÷ 8 = **675 clips**

---

## Production Cost Scenarios

### Scenario 1: Perfect First Takes (Optimistic)

**Assumptions:**
- 1 generation per clip
- All clips usable first try
- No reshoots needed

**Calculations:**
- Clips: 675
- Generation time: 5 min/clip × 675 = 3,375 minutes = **56.25 hours**
- Cost at $3.44/hr: **$193.50**

**Reality check:** 🚫 Unrealistic - will need multiple takes

---

### Scenario 2: 3 Takes Per Clip (Realistic)

**Assumptions:**
- Generate 3 versions per clip
- Select best one
- ~90% usability rate

**Calculations:**
- Total videos to generate: 675 × 3 = **2,025 videos**
- Generation time: 5 min/video × 2,025 = 10,125 minutes = **168.75 hours**
- GPU time needed: **168.75 hours**
- Cost on H200: 168.75 × $3.44 = **$580.50**

**Timeline:**
- Single H200: 168.75 hours = **7 days continuous**
- H200 x8: 168.75 ÷ 8 = 21 hours = **< 1 day**

---

### Scenario 3: 5 Takes Per Clip (Professional)

**Assumptions:**
- Generate 5 versions per clip
- Director's choice of best take
- Creative flexibility

**Calculations:**
- Total videos: 675 × 5 = **3,375 videos**
- Generation time: 3,375 × 5 min = 16,875 minutes = **281.25 hours**
- Cost on H200: 281.25 × $3.44 = **$967.50**

**Timeline:**
- Single H200: 281.25 hours = **11.7 days**
- H200 x8: 281.25 ÷ 8 = 35 hours = **1.5 days**

---

### Scenario 4: 10 Takes Per Clip (Perfectionist)

**Assumptions:**
- 10 versions per clip
- Maximum creative options
- A/B testing for quality

**Calculations:**
- Total videos: 675 × 10 = **6,750 videos**
- Generation time: 6,750 × 5 min = 33,750 minutes = **562.5 hours**
- Cost on H200: 562.5 × $3.44 = **$1,935.00**

**Timeline:**
- Single H200: 562.5 hours = **23.4 days**
- H200 x8: 562.5 ÷ 8 = 70 hours = **3 days**

---

## Cost Summary Table

| Takes/Clip | Total Videos | GPU Hours | H200 Cost | H200 x8 Cost | Timeline (x1) | Timeline (x8) |
|------------|-------------|-----------|-----------|--------------|---------------|---------------|
| 1 (unrealistic) | 675 | 56.25 | $193.50 | $193.50 | 2.3 days | 7 hours |
| **3 (realistic)** | **2,025** | **168.75** | **$580.50** | **$580.50** | **7 days** | **21 hours** |
| 5 (professional) | 3,375 | 281.25 | $967.50 | $967.50 | 11.7 days | 35 hours |
| 10 (perfectionist) | 6,750 | 562.5 | $1,935.00 | $1,935.00 | 23.4 days | 70 hours |

---

## Comparison with Traditional Production

### Traditional Film Production

**Costs for 90-minute feature:**
- Ultra-low budget: $100,000 - $500,000
- Low budget: $500,000 - $2,000,000
- Mid budget: $2,000,000 - $20,000,000
- Studio film: $20,000,000+

**For reference:**
- Day rate for small crew: $5,000-10,000/day
- 90-minute shoot: 10-30 days minimum
- Post-production: Months of work
- **Minimum realistic budget: $50,000-100,000**

### HunyuanVideo AI Production

**Costs:**
- 3 takes/clip: **$580.50** (99.4% savings)
- 10 takes/clip: **$1,935.00** (98% savings)

**Savings: 95-99% vs traditional production**

---

## Recommended Production Workflow

### Phase 1: Pre-Production (Week 1)
**Cost: $0**
- Write detailed shot list (675 clips)
- Craft prompts for each scene
- Storyboard sequence
- Plan transitions
- Define style guide

### Phase 2: Initial Generation (Week 2)
**Setup: H200 x1 @ $3.44/hr**
- Generate 3 takes per clip: **$580.50**
- Review and select best clips
- Identify clips needing regeneration
- Timeline: 7 days continuous

### Phase 3: Reshoots (Week 3)
**Setup: H200 x1 @ $3.44/hr**
- Regenerate ~20% of clips (5-10 takes each): **$300-500**
- Refine prompts based on Phase 2 learnings
- Generate alternative versions

### Phase 4: Post-Production (Week 4)
**Cost: $0 (using existing tools)**
- Stitch clips together (FFmpeg, Premiere, DaVinci Resolve)
- Add transitions
- Color grading pass
- Audio track (music/dialogue)
- Final render

---

## Total Project Cost Breakdown

### Budget Option (H200 x1)
```
GPU Droplet Setup:        $0 (one-time, reusable)
Phase 2 - Initial Gen:    $580.50 (7 days @ $82.56/day)
Phase 3 - Reshoots:       $400.00 (estimated)
Post-production:          $0 (open-source tools)
─────────────────────────────────────────
TOTAL GPU:                $980.50

Plus optional:
- Professional editor:    $1,000-5,000
- Sound design:           $500-2,000
- Music licensing:        $500-5,000
─────────────────────────────────────────
REALISTIC TOTAL:          $3,000-13,000
```

### Speed Option (H200 x8)
```
GPU Droplet Setup:        $0
Phase 2 - Initial Gen:    $580.50 (21 hours)
Phase 3 - Reshoots:       $400.00 (6 hours)
─────────────────────────────────────────
TOTAL GPU:                $980.50

Complete in 27 hours (1-2 days)
```

---

## Cost Comparison: Self-Hosted vs Cloud APIs

### Veo 3.1 Fast API
```
Per 8-second video:       $0.80 (8 sec × $0.10/sec)
3 takes × 675 clips:      2,025 videos × $0.80 = $1,620
10 takes × 675 clips:     6,750 videos × $0.80 = $5,400
```

**HunyuanVideo saves:** $1,039-3,465 vs Veo 3.1 Fast

### Veo 3.1 Standard API
```
Per 8-second video:       $1.60 (8 sec × $0.20/sec)
3 takes × 675 clips:      2,025 videos × $1.60 = $3,240
10 takes × 675 clips:     6,750 videos × $1.60 = $10,800
```

**HunyuanVideo saves:** $2,659-8,865 vs Veo 3.1 Standard

### HunyuanVideo Self-Hosted Summary
```
3 takes × 675 clips:      $580.50 (64% cheaper than Veo Fast)
10 takes × 675 clips:     $1,935.00 (64% cheaper than Veo Fast)
```

---

## Technical Considerations

### HunyuanVideo Limitations & Workarounds

⚠️ **Current max: 129 frames**
- At 30fps = 4.3 seconds
- At 15fps = 8.6 seconds ✅ (works for 8-sec clips!)

### Solutions for 8-Second Clips

**Option 1: Generate at 15fps** (Recommended)
- Get 8.6 seconds per video
- Lower frame rate = smoother motion perception
- Post-production frame blending if needed

**Option 2: Stitch Two 4.3-Second Clips**
- Generate 1,350 clips instead of 675
- Use cross-dissolve transitions
- More time/cost but higher frame rate

**Option 3: Use H200's Extra VRAM**
- With 141GB VRAM, may support 200+ frames
- Experimental: test before committing
- Could enable 6.6 seconds @ 30fps

---

## Quality Guidelines

### Consistency Across Clips

**Prompt Engineering:**
```
Style guide: "cinematic, 35mm film, warm color grade, shallow depth of field"
Scene 1: "[style guide], establishing shot of city skyline at sunset"
Scene 2: "[style guide], medium shot of protagonist walking down street"
Scene 3: "[style guide], close-up of protagonist's face, contemplative"
```

**Best Practices:**
- Use consistent style descriptors
- Maintain lighting continuity
- Plan shot types in advance
- Use prompt rewrite (Master mode) for high quality

### Post-Production Color Grading

- Apply LUT (Look-Up Table) across all clips
- Normalize exposure and contrast
- Match white balance
- Add film grain for consistency

---

## Recommended Production Approaches

### Approach 1: Budget Indie Film ($1,000-3,000)

**Setup:**
- H200 x1 running on-demand
- 2-3 weeks GPU time
- Open-source post-production tools

**Process:**
1. Week 1: Generate 3 takes per clip (675 × 3 = 2,025 videos)
2. Week 2: Review and regenerate problem clips
3. Week 3: Post-production editing
4. Week 4: Sound design and final render

**Cost breakdown:**
- GPU: $580-1,000
- Software: $0 (DaVinci Resolve Free, Audacity)
- Music: $0-500 (royalty-free or license)
- **Total: $1,000-3,000**

---

### Approach 2: Fast-Track Production (3-4 days, $1,000-1,500)

**Setup:**
- H200 x8 for maximum speed
- Professional team working in parallel

**Process:**
- Day 1: Generate 5 takes per clip (complete in 35 hours)
- Day 2: Review, select, regenerate issues
- Day 3: Edit and stitch
- Day 4: Final polish and render

**Cost breakdown:**
- GPU: $980-1,200
- Rush post-production: $500-1,000
- **Total: $1,500-2,200**

**Best for:** Time-sensitive projects, festival deadlines

---

### Approach 3: Professional Quality ($2,500-7,500)

**Setup:**
- H200 x1 running 24/7 for 1 month
- Professional editor and sound designer
- Unlimited regenerations

**Process:**
- Week 1: Pre-production and prompt crafting
- Week 2-3: Generate 10 takes per clip, review continuously
- Week 4: Professional editing and sound design
- Additional time for revisions

**Cost breakdown:**
- GPU: $2,511 (30 days 24/7)
- Professional editor: $2,000-3,000
- Sound designer: $1,000-2,000
- Music licensing: $500-2,000
- **Total: $6,000-10,000**

**Best for:** High-quality festival submissions, commercial release

---

## Alternative: On-Demand Production Strategy

**Minimize costs by running GPU only when actively generating:**

```
Week 1: Setup & test (2 days × 24hr)             $165
Week 2: Generate 2,025 clips (7 days × 24hr)     $580
Week 3: Reshoots (3 days × 8hr)                  $83
─────────────────────────────────────────────────
TOTAL:                                            $828

vs continuous H200 @ $2,511/month
Savings: $1,683 (67% reduction)
```

**Implementation:**
- Use DigitalOcean API automation
- Start droplet when ready to generate batch
- Stop when reviewing/editing
- Restart for reshoots

---

## ROI Analysis

### Traditional Production
- **Cost:** $50,000-100,000 minimum
- **Time:** 3-6 months
- **Crew:** 10-50 people
- **Equipment rental:** $10,000+
- **Locations:** $5,000-20,000
- **Post-production:** $10,000-50,000

### AI Production with HunyuanVideo
- **Cost:** $1,000-3,000
- **Time:** 4-6 weeks
- **Crew:** 1-3 people (director, editor, sound)
- **Equipment:** $0 (cloud GPU)
- **Locations:** $0 (all AI-generated)
- **Post-production:** $0-2,000

### **Savings: 95-98%**
### **Time savings: 50-75%**

---

## Distribution & Monetization

### Festival Circuit
- Entry fees: $50-150 per festival
- Target 10-20 festivals: $1,000-3,000
- **Total investment:** $2,000-6,000
- Potential prize money: $1,000-100,000+

### Streaming Platforms
- Self-distribution (YouTube, Vimeo): $0
- Amazon Prime Video Direct: Revenue share
- Tubi, Plex: Revenue share
- **No upfront costs**

### Direct Sales
- Sell via Vimeo On Demand
- Price: $3.99-9.99 rental, $9.99-19.99 purchase
- Need: 300-2,000 sales to break even
- Viral potential: Unlimited upside

### Case Study: "$3,000 AI Movie"
```
Production cost:          $3,000
Festival submission:      $1,500
Marketing:                $1,000
─────────────────────────
TOTAL INVESTMENT:         $5,500

Break-even scenarios:
- 550 rentals @ $9.99
- 275 purchases @ $19.99
- Or: Win one festival prize
- Or: Streaming deal advance
```

---

## Risk & Mitigation

### Technical Risks

**Risk:** Inconsistent visual style across clips
- **Mitigation:** Detailed style guide, consistent prompts, color grading

**Risk:** 8-second limit doesn't work
- **Mitigation:** Test first 10 clips before full production, use frame rate adjustment

**Risk:** GPU availability issues
- **Mitigation:** Reserve GPU capacity, have backup cloud API plan

### Creative Risks

**Risk:** AI-generated content lacks emotional depth
- **Mitigation:** Strong script, creative editing, professional sound design

**Risk:** Audience rejects AI content
- **Mitigation:** Market as experimental/unique, target tech-forward audiences

### Financial Risks

**Risk:** Project goes over budget
- **Mitigation:** Phase production, stop if early results unsatisfactory

**Risk:** No distribution interest
- **Mitigation:** Self-distribute online, build audience first

---

## Success Metrics

### Production Phase
- ✅ Generate 2,000+ clips within budget
- ✅ 90%+ usable clip rate
- ✅ Stay under $3,000 for GPU costs
- ✅ Complete in 4-6 weeks

### Post-Production Phase
- ✅ Seamless clip transitions
- ✅ Consistent visual style
- ✅ Professional sound design
- ✅ 90-minute final runtime

### Distribution Phase
- ✅ Submit to 10+ festivals
- ✅ 1,000+ online views in first month
- ✅ Positive audience reception
- ✅ Break-even within 12 months

---

## Final Recommendations

### Best Approach for First-Time AI Filmmakers

**Budget: $1,500-3,000**
**Timeline: 6 weeks**

1. **Week 1: Pre-production**
   - Write detailed shot list
   - Craft and test prompts
   - Create storyboard

2. **Week 2-3: Generation**
   - Use H200 x1 on-demand
   - Generate 3 takes per clip
   - Review and regenerate
   - Cost: $580-1,000

3. **Week 4-5: Post-production**
   - Edit and stitch clips
   - Color grading
   - Sound design
   - Cost: $0-1,000 (DIY or freelancer)

4. **Week 6: Final polish**
   - Music
   - Final render
   - Festival submissions

**Total cost: $1,500-3,000**
**Risk level: Low**
**Learning opportunity: High**

---

## Conclusion

**A 90-minute AI-generated feature film is now financially viable at $1,000-3,000**, representing a **95-98% cost reduction** from traditional production.

**Key enablers:**
- Self-hosted GPU @ $3.44/hr
- Multiple takes per clip (3-10x)
- Fast iteration (5 min per video)
- Open-source post-production tools

**This democratizes filmmaking**, allowing independent creators to produce feature-length content at a fraction of traditional costs, opening new possibilities for experimental and diverse storytelling.

---

## Additional Resources

- See [COST_COMPARISON.md](COST_COMPARISON.md) for API alternatives
- See [GPU_SELECTION_GUIDE.md](GPU_SELECTION_GUIDE.md) for hardware options
- See [USE_CASES.md](USE_CASES.md) for more business applications
- See [README.md](README.md) for deployment instructions
