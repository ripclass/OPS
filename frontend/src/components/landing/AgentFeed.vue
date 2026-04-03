<template>
  <section ref="targetRef" class="feed-shell" :class="{ 'feed-shell--visible': isVisible }">
    <div class="feed-heading">Live agent feed</div>
    <div class="feed-window">
      <div class="feed-track">
        <div class="feed-group" v-for="group in 2" :key="group">
          <article v-for="(post, index) in posts" :key="`${group}-${index}`" class="feed-post">
            <div class="feed-post__meta">{{ post.meta }}</div>
            <p class="feed-post__content" :class="contentClass(post)">
              {{ post.content }}
            </p>
          </article>
        </div>
      </div>
    </div>
    <p class="feed-footnote">This simulation ran 90 seconds ago. None of these people exist. All of them are real.</p>
  </section>
</template>

<script setup>
import { useRevealOnScroll } from '../../composables/useRevealOnScroll'

defineProps({
  posts: {
    type: Array,
    required: true,
  },
})

const { targetRef, isVisible } = useRevealOnScroll()

const contentClass = (post) => {
  return {
    'feed-post__content--mono': post.tone === 'mono',
    'feed-post__content--bengali': post.language === 'bengali',
    'feed-post__content--devanagari': post.language === 'devanagari',
    'feed-post__content--arabic': post.language === 'arabic',
    'feed-post__content--tamil': post.language === 'tamil',
  }
}
</script>

<style scoped>
.feed-shell {
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.feed-shell--visible {
  opacity: 1;
  transform: translateY(0);
}

.feed-heading {
  margin-bottom: 18px;
  color: var(--murmur-text-muted);
  font-family: var(--murmur-font-mono);
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.feed-window {
  position: relative;
  height: 420px;
  overflow: hidden;
  border-top: 1px solid var(--murmur-border);
  border-bottom: 1px solid var(--murmur-border);
}

.feed-window::before,
.feed-window::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  height: 48px;
  z-index: 1;
  pointer-events: none;
}

.feed-window::before {
  top: 0;
  background: linear-gradient(180deg, var(--murmur-bg-primary), transparent);
}

.feed-window::after {
  bottom: 0;
  background: linear-gradient(0deg, var(--murmur-bg-primary), transparent);
}

.feed-track {
  display: flex;
  flex-direction: column;
  animation: feed-scroll 54s linear infinite;
}

.feed-group {
  display: flex;
  flex-direction: column;
}

.feed-post {
  padding: 20px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.feed-post__meta {
  margin-bottom: 8px;
  color: var(--murmur-text-agent-name);
  font-family: var(--murmur-font-mono);
  font-size: 11px;
  letter-spacing: 0.08em;
}

.feed-post__content {
  margin: 0;
  color: var(--murmur-text-primary);
  font-family: var(--murmur-font-body);
  font-size: 17px;
  line-height: 1.7;
  white-space: pre-wrap;
}

.feed-post__content--mono {
  font-family: var(--murmur-font-mono);
}

.feed-post__content--bengali {
  font-family: var(--murmur-font-script-bengali);
}

.feed-post__content--devanagari {
  font-family: var(--murmur-font-script-devanagari);
}

.feed-post__content--arabic {
  font-family: var(--murmur-font-script-arabic);
}

.feed-post__content--tamil {
  font-family: var(--murmur-font-script-tamil);
}

.feed-footnote {
  margin: 16px 0 0;
  color: var(--murmur-text-muted);
  font-size: 15px;
  line-height: 1.7;
}

@keyframes feed-scroll {
  from {
    transform: translateY(0);
  }

  to {
    transform: translateY(-50%);
  }
}

@media (prefers-reduced-motion: reduce) {
  .feed-track {
    animation: none;
  }
}

@media (max-width: 640px) {
  .feed-window {
    height: 360px;
  }

  .feed-post__content {
    font-size: 16px;
  }
}
</style>
