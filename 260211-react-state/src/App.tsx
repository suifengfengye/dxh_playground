import React from 'react';
import { JotaiDemoV3 } from './components/JotaiDemoV3';
// import { JotaiDemoV2 } from './components/JotaiDemoV2';
// import { JotaiDemo } from './components/JotaiDemo';
// import { ZustandDemoV3 } from './components/ZustandDemoV3';
// import { ZustandDemoV2 } from './components/ZustandDemoV2';
// import { ZustandDemo } from './components/ZustandDemo';
// import { UseReducerDemoV3 } from './components/UseReducerDemoV3';
// import { UseReducerDemoV2 } from './components/UseReducerDemoV2';
// import { UseReducerDemo } from './components/UseReducerDemo';
import { ReduxDemo1 } from './my-redux1/ReduxDemo1' 

const App = () => {
    return (
        <div>
            {/* <UseReducerDemo /> */}
            {/* <UseReducerDemoV2 /> */}
            {/* <UseReducerDemoV3 /> */}
            {/* <ZustandDemo /> */}
            {/* <ZustandDemoV2 /> */}
            {/* <ZustandDemoV3 /> */}
            {/* <JotaiDemo /> */}
            {/* <JotaiDemoV2 /> */}
            {/* <JotaiDemoV3 /> */}
            <ReduxDemo1 />
        </div>
    );
}

export default App;