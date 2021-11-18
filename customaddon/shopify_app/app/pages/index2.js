import {Button, Card,TextField, TextStyle, EmptyState, Layout, Page } from '@shopify/polaris';
import React, { useState, useCallback} from 'react';
// import { Alert } from 'reactstrap';

class Hello extends React.Component {
    constructor(){
        super();
        this.state = {
            message: "my friend (from state)!"
        };
        this.updateMessage = this.updateMessage.bind(this);
    }
    updateMessage() {
        this.setState({
            message: "my friend (from changed state)!"

        });
    }

    render() {
        return (
            <Page>
                <Layout>
                <Button outline>Settings</Button>
                <h1>Hello {this.state.message}!</h1>
                <button onClick={this.updateMessage}>Click me!</button>
                    <Button outline>Add product</Button>
                </Layout>
                <AnnotatedLayoutDiscount />
                <AnnotatedLayoutPrice />
            </Page>
        )
    }

}

const Index = () => (
    <Hello />
);

export default Index;

// class AnnotatedLayoutDiscount extends React.Component {
//   state = {};
//
//   render() {
//     return (
//       <Page>
//         <Layout>
//           <Layout.AnnotatedSection
//             title="Default discount"
//             description="Add a product to Sample App, it will automatically be discounted."
//           >
//             <Card sectioned>
//               <div>Card</div>
//             </Card>
//           </Layout.AnnotatedSection>
//         </Layout>
//       </Page>
//     );
//   }
// }
//
// class AnnotatedLayoutPrice extends React.Component {
//   state = {};
//
//   render() {
//     return (
//       <Page>
//         <Layout>
//           <Layout.AnnotatedSection
//             title="Prices"
//             description="Add a product Price"
//           >
//             <Card sectioned>
//               <div>0 VND</div>
//             </Card>
//           </Layout.AnnotatedSection>
//         </Layout>
//       </Page>
//     );
//   }
// }