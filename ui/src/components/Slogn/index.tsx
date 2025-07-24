import Lottie from 'react-lottie';
import { animationData } from './animation';

const Slogn: GenieType.FC = () => {
  const defaultOptions = {
    loop: true,
    autoplay: true,
    animationData: animationData,
    rendererSettings: {
      preserveAspectRatio: 'xMidYMid slice',
      className: 'lottie'
    },
  };
  return (
    <div className='mb-54'>
      <Lottie options={defaultOptions}
        height={68}
        width={200}
      />
    </div>

  );
};

export default Slogn;
