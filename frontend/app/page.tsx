import NetworkSection from './components/NetworkSection';
import ProjectsSection from './components/ProjectsSection';

const VIDEO_ID = '0L8953RVKGU';

export default function Home() {
  return (
    <>
      <div className="landing">
        <div className="landing-video">
          <iframe
            src={`https://www.youtube.com/embed/${VIDEO_ID}?autoplay=1&mute=1&loop=1&playlist=${VIDEO_ID}&controls=0&rel=0&modestbranding=1&playsinline=1`}
            allow="autoplay; encrypted-media"
            title="Vidéo de fond Cultur'all"
          />
        </div>
      </div>
      <ProjectsSection />
      <NetworkSection />
    </>
  );
}
