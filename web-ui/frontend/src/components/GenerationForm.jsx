import { useState } from 'react';
import { Sparkles, Settings, Video } from 'lucide-react';

export default function GenerationForm({ onGenerate, generating }) {
  const [formData, setFormData] = useState({
    prompt: '',
    video_size: 720,
    video_length: 129,
    infer_steps: 50,
    seed: null,
    cfg_scale: 6.0,
    flow_reverse: true
  });

  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    onGenerate(formData);
  };

  const promptExamples = [
    "A cat walks on the grass, realistic style",
    "Drone shot of ocean waves crashing on a beach at sunset",
    "Time-lapse of clouds moving over a mountain landscape",
    "A butterfly landing on a flower in slow motion",
    "City street at night with neon lights and rain"
  ];

  return (
    <form onSubmit={handleSubmit} className="card space-y-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-primary-500/10 rounded-lg">
          <Sparkles className="w-6 h-6 text-primary-500" />
        </div>
        <h2 className="text-2xl font-bold">Generate Video</h2>
      </div>

      {/* Prompt */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Prompt
          <span className="text-red-500 ml-1">*</span>
        </label>
        <textarea
          value={formData.prompt}
          onChange={(e) => setFormData({ ...formData, prompt: e.target.value })}
          placeholder="Describe the video you want to generate..."
          className="input w-full h-32 resize-none"
          required
        />
        
        {/* Example prompts */}
        <div className="mt-2 flex flex-wrap gap-2">
          {promptExamples.map((example, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setFormData({ ...formData, prompt: example })}
              className="text-xs bg-dark-hover hover:bg-dark-border px-3 py-1 rounded-full transition-colors"
            >
              {example.slice(0, 30)}...
            </button>
          ))}
        </div>
      </div>

      {/* Quick Settings */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            <Video className="inline w-4 h-4 mr-1" />
            Resolution
          </label>
          <select
            value={formData.video_size}
            onChange={(e) => setFormData({ ...formData, video_size: parseInt(e.target.value) })}
            className="input w-full"
          >
            <option value={540}>540p (Faster)</option>
            <option value={720}>720p (Better Quality)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Frames
          </label>
          <input
            type="number"
            min={1}
            max={129}
            value={formData.video_length}
            onChange={(e) => setFormData({ ...formData, video_length: parseInt(e.target.value) })}
            className="input w-full"
          />
          <p className="text-xs text-gray-500 mt-1">~5 seconds at 25fps</p>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Quality Steps
          </label>
          <input
            type="number"
            min={30}
            max={100}
            value={formData.infer_steps}
            onChange={(e) => setFormData({ ...formData, infer_steps: parseInt(e.target.value) })}
            className="input w-full"
          />
          <p className="text-xs text-gray-500 mt-1">Higher = better quality</p>
        </div>
      </div>

      {/* Advanced Settings */}
      <button
        type="button"
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
      >
        <Settings className="w-4 h-4" />
        {showAdvanced ? 'Hide' : 'Show'} Advanced Settings
      </button>

      {showAdvanced && (
        <div className="space-y-4 p-4 bg-dark-hover rounded-lg border border-dark-border">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Random Seed
              </label>
              <input
                type="number"
                value={formData.seed || ''}
                onChange={(e) => setFormData({ ...formData, seed: e.target.value ? parseInt(e.target.value) : null })}
                placeholder="Random (leave empty)"
                className="input w-full"
              />
              <p className="text-xs text-gray-500 mt-1">For reproducible results</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                CFG Scale
              </label>
              <input
                type="number"
                min={1}
                max={20}
                step={0.5}
                value={formData.cfg_scale}
                onChange={(e) => setFormData({ ...formData, cfg_scale: parseFloat(e.target.value) })}
                className="input w-full"
              />
              <p className="text-xs text-gray-500 mt-1">Guidance strength (6.0 recommended)</p>
            </div>
          </div>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.flow_reverse}
              onChange={(e) => setFormData({ ...formData, flow_reverse: e.target.checked })}
              className="w-4 h-4 rounded bg-dark-card border-dark-border"
            />
            <span className="text-sm">Enable Flow Reversal (Recommended)</span>
          </label>
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={generating || !formData.prompt.trim()}
        className="btn-primary w-full flex items-center justify-center gap-2"
      >
        {generating ? (
          <>
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Generating...
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5" />
            Generate Video
          </>
        )}
      </button>

      {/* Cost Estimate */}
      <div className="text-center text-sm text-gray-400">
        <p>
          Estimated cost: <span className="text-primary-500 font-medium">$0.29</span>
          {' '}• Duration: <span className="text-primary-500 font-medium">~5 min</span>
        </p>
      </div>
    </form>
  );
}
