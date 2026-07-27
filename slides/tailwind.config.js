/** Tailwind is used only for utility classes (grid/flex/panels) inside Marp slides.
 * Preflight is disabled so it doesn't clobber Marp theme base styles (h1/ul/etc). */
module.exports = {
  content: ["./*.md"],
  corePlugins: {
    preflight: false,
  },
  theme: {
    extend: {},
  },
  plugins: [],
};
