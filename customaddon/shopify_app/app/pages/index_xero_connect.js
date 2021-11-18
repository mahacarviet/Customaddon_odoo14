import { Link, Thumbnail, Button,MediaCard, Frame,FormLayout, Layout, Page, AppProvider } from '@shopify/polaris';
import React, {Component} from 'react';
import ReactDOM from "react-dom";
import '@shopify/polaris/dist/styles.css';
import translations from '@shopify/polaris/locales/en.json';
import image from './connector.png';

class Main extends Component{

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <AppProvider i18n={translations}>
                <Frame>
                    <Page>
                        <div style={{ marginLeft: 'auto', marginRight: 'auto', width: '50%', display:'inline'}}>
                            <img style={{paddingTop:'20px', paddingLeft:'10px'}} src={image} alt="Connect to Xero" width="640px" height="360px" />
                            <div style={{paddingLeft:'30px', display:'inline'}} >
                                <Button onClick={event =>  window.top.location.href="/xero_connect"} primary>Connect To Xero</Button>
                            </div>
                        </div>
                        <div style={{marginTop:'30px' ,marginLeft: 'auto', marginRight: 'auto', width: '50%'}}>
                            <ol>
                                <li><Link onClick={event =>  window.top.location.href="https://www.xero.com/signup/"}>Signup an account</Link> if you haven't already</li>
                                <li>Click "Connect to Xero"</li>
                                <li>Login to Xero if you haven't already</li>
                                <li>Click "Accept" to start connecting to the application</li>
                                <li>Start Exporting data to your Xero Account</li>
                            </ol>
                        </div>
                    </Page>
                </Frame>
            </AppProvider>
        )
    }
}

export default Main;

const wrapper = document.getElementById("xero_connect");
wrapper ? ReactDOM.render(<Main />, wrapper) : false;





