import HeroVideo from './components/HeroVideo';
import NetworkSection from './components/NetworkSection';
import ProjectsSection from './components/ProjectsSection';

export default function Home() {
  return (
    <>
      <div className="landing">
        <div className="landing-video">
          <HeroVideo />
        </div>
      </div>
      <ProjectsSection />
      <NetworkSection />
    </>
  );
}
