import ReactDOM from "react-dom";
import React from 'react';
import instagramIcon from '../images/instagram.png';
import {ResourcePicker} from '@shopify/app-bridge-react';
import translations from '@shopify/polaris/locales/en.json';
import fetch from 'isomorphic-fetch';
import {CopyToClipboard} from 'react-copy-to-clipboard';
import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import "../css/af-insta-style.css";
import "../css/polaris.css";
import {getUrl} from "../base";
import {
    AppProvider,
    Button,
    Modal,
    ButtonGroup
} from '@shopify/polaris';
let _ = require('underscore');

let $ = null;
if (typeof window !== "undefined") {
    import('jquery').then((module) => {
        $ = module.default;
    });
    import ('jquery-ui/ui/widgets/mouse');
    import ('jquery-ui/ui/widgets/draggable');
}

let appConfig = {};

class InstagramSlider extends React.Component {
    retrievedFlag = false;

    constructor(props) {
        super(props);
        appConfig = props.appConfig ? props.appConfig : false;
        this.state = {
            open: false,
            current_media: {},
            product_picker_open: false,
            loader: false,
            medias: [],
            slider_settings: {
                enablePopup: '0',
                feedLabel: '',
                slidesPerRow: 3,
                rows: 3,
                slidesToScroll: 1,
                dots: false,
                infinite: false,
                speed: 700,
                lazyLoad: true,
                arrows: true,
                draggable: false,
                responsive: [
                    {
                        breakpoint: 600,
                        settings: {
                            slidesPerRow: 2,
                            dots: false,
                            rows: 1
                        }
                    }
                ]
            },
            is_product_slider: typeof props.isProductSlider !== "undefined" ? props.isProductSlider : false
        };
        this.retrieveSettings();
    }

    findNextMedia() {
        const currentMedia = this.state.current_media;
        const index = this.state.medias.findIndex(media => media.id === currentMedia.id);
        if (typeof this.state.medias[index + 1] !== 'undefined') {
            return this.state.medias[index + 1];
        }
        return false;
    }

    findPrevMedia() {
        const currentMedia = this.state.current_media;
        const index = this.state.medias.findIndex(media => media.id === currentMedia.id);
        if (typeof this.state.medias[index - 1] !== 'undefined') {
            return this.state.medias[index - 1];
        }
        return false;
    }

    nextMedia() {
        const nextMedia = this.findNextMedia()
        if (nextMedia) {
            this.state.current_media = nextMedia;
            this.setState(this.state);
        }
    }

    prevMedia() {
        const prevMedia = this.findPrevMedia()
        if (prevMedia) {
            this.state.current_media = prevMedia;
            this.setState(this.state);
        }
    }

    activeHotSpotEdit() {
        var self = this;
        $('.popup_image_container .dot').draggable({
            containment: ".popup_image_container",
            stop: function (event, ui) {
                var new_left_perc = parseInt($(this).css("left")) / ($(".popup_image_container").width() / 100);
                var new_top_perc = parseInt($(this).css("top")) / ($(".popup_image_container").height() / 100);

                $(this).css("left", new_left_perc + "%");
                $(this).css("top", new_top_perc + "%");

                console.log("Left: " + new_left_perc + "%; Top: " + new_top_perc + '%;');
                self.saveHotspot({
                    id: $(this).data('id'),
                    top_perc: new_top_perc,
                    left_perc: new_left_perc,
                    media: self.state.current_media
                })
            }
        });
    }

    generateHotspotsHtml(hotspots) {
        hotspots = hotspots || [];
        return hotspots.map((value, index) => {
            return (
                <div key={index} className="dot" data-id={value['id']}
                     onMouseEnter={() => {
                         $('.tagged_product').addClass('tagged_product_blurred');
                         $('.tagged_product[data-id="'+value['id']+'"]').removeClass('tagged_product_blurred');
                     }}
                     onMouseLeave={() => {
                         $('.tagged_product').removeClass('tagged_product_blurred');
                     }}
                     style={{top: value['top_percent'] + "%", left: value['left_percent'] + "%"}}>
                    {index + 1}
                </div>
            )
        })
    }

    handleBuyClick(data){
        var self = this;
        return $.ajax(
            'analytic/add_to_card',
            {
                method: 'POST',
                dataType: 'json',
                data: JSON.stringify({
                    params: data
                }),
                contentType: 'application/json',
            }
        ).done(() => {
            console.log("True")
        }).fail(() => {
            console.log("Fasle")
        })
    }

    generateTaggedProductsHtml(hotspots) {
        var self = this;
        hotspots = hotspots || [];
        var hidePrice = true;

        return hotspots.map((value, index) => {
            if (hidePrice) {
                $('.p_price').hide();
                hidePrice = false;
            }
            $.ajax(
                value['product_url'] + '.js',
                {
                    method: 'GET'
                }
            ).done((res) => {
                var priceHolder = $('.p_price[data-price-id="'+value['id']+'"]');
                priceHolder.text('');
                try {
                    res = JSON.parse(res);
                    var price = (res.price/100).toFixed(2);
                    var currency = "<Currency>";
                    if (typeof Shopify !== "undefined" && typeof Shopify.currency !== "undefined") {
                        currency = Shopify.currency.active;
                    }
                    priceHolder.text(' - ' + price + ' ' + currency);
                    priceHolder.show();
                } catch (e) {
                    console.log(e);
                    console.log(res);
                }
            }).fail((res) => {
                $('.p_price[data-price-id="'+value['id']+'"]').text('');
                console.log(res);
            })

            if (value['product_name'].length > 30) {
                value['product_name'] = value['product_name'].substring(0, 30) +'...';
            }

            return (
                <div key={index} className="tagged_product" data-id={value['id']}
                     onMouseEnter={() => {
                         $('.popup_image_container .dot[data-id="'+value['id']+'"]').css('opacity', 0.7);
                     }}
                     onMouseLeave={() => {
                         $('.popup_image_container .dot[data-id="'+value['id']+'"]').css('opacity', '');
                     }} >
                    <a>
                        <img className="p_thumbnail" src={value['product_image_url']}/>
                        <span className="p_name">{value['product_name']}
                            <span className="p_price" data-price-id={value['id']}> </span>
                        </span>
                        <button className="p_addtocart" onClick={() => {
                            self.handleBuyClick({
                                  media_id: self.state.current_media.id,
                                  product_handle: value['product_handle'],
                                    })
                                }}>BUY</button>
                    </a>
                    {(() => {
                        if (this.isBackend()) {
                            return (
                                <div className="delete" onClick={() => {
                                    self.saveHotspot({
                                        id: value['id'],
                                        media: self.state.current_media,
                                        delete: true
                                    })
                                }}>Delete
                                </div>
                            )
                        }
                    })()}
                </div>
            )
        })
    }

    isProductSlider() {
        return typeof this.state.is_product_slider !== "undefined" && this.state.is_product_slider;
    }

    isBackend() {
        return !_.isEmpty(appConfig);
    }

    renderItems() {
        return this.state.medias.map((value, index) => {
            return (
                <div key={index} className="media_wrapper" onClick={() => {
                    if (this.state.slider_settings.enablePopup === '0') {
                        window.open(value.permalink, '_blank');
                    } else {
                        this.state.open = true;
                        this.state.current_media = value;
                        this.setState(this.state);
                    }
                }}>
                    <div className={!value.show && this.isBackend() ? 'image_wrapper media_hidden' : 'image_wrapper'}>
                        <img src={value.media_type === 'VIDEO' ? value.thumbnail_url : value.media_url} onError={() => {
                            this.state.medias = this.state.medias.filter((media) => {
                                return media['id'] !== value.id
                            });
                            this.setState(this.state);
                        }}/>
                        <div className="overlay">
                            <img src={instagramIcon}/>
                        </div>
                    </div>
                </div>
            );
        })

    }

    resourcePicker() {
        if (this.isBackend()) {
            return (
                <ResourcePicker
                    resourceType="Product"
                    showVariants={false}
                    allowMultiple={false}
                    open={this.state.product_picker_open}
                    onSelection={(resources) => this.handleProductSelection(resources)}
                    onCancel={() => {
                        this.state.product_picker_open = false;
                        this.setState(this.state);
                    }}
                />
            )
        }
        return null;
    }

    listenToKeyDown() {
        $(document).off('keydown.popup');
        $(document).on('keydown.popup', function(e){
            if (e.keyCode == '37') {
               // left arrow
                $('.popup_nav .prev').click();
            }
            else if (e.keyCode == '39') {
               // right arrow
                $('.popup_nav .next').click();
            }
        })
    }

    render() {
        return (
            <AppProvider i18n={translations}>
                <div id="af_slider" style={{
                    margin: 'auto', width: this.state.slider_settings.width + '%'
                }}>
                    {(() => {
                        if (this.state.medias.length > 0 && this.state.slider_settings.feedLabel) {
                            return (
                                <span className="feed_label">{this.state.slider_settings.feedLabel}</span>
                            )
                        }
                    })()}

                    <div id="slider_wrapper" className={this.state.slider_settings.feedLayout == 2 && !this.isProductSlider()? 'slider_nine': ''}>
                        <Slider {...this.state.slider_settings}>
                            {this.renderItems()}
                        </Slider>
                    </div>
                </div>
                <Modal
                    large={true}
                    instant={true}
                    open={this.state.open}
                    onClose={() => {
                        this.state.open = false;
                        this.setState(this.state);
                    }}
                >
                    <div id="af_insta_popup" onLoadStart={this.listenToKeyDown} onLoad={this.listenToKeyDown}>
                        <div className={!this.state.current_media.show && this.isBackend()? 'popup_image_container media_hidden': 'popup_image_container'} onMouseEnter={(() => {
                            if (this.isBackend()) {
                                return this.activeHotSpotEdit.bind(this);
                            }
                            return null;
                        })()}>
                            {(() => {
                                if (this.state.current_media.media_type === 'VIDEO') {
                                    return <video controls poster={this.state.current_media.thumbnail_url} >
                                        <source src={this.state.current_media.media_url} type="video/mp4" />
                                    </video>
                                } else {
                                    return <img src={this.state.current_media.media_url} />
                                }
                            })()}

                            <div className="dot_container">
                                {this.generateHotspotsHtml(this.state.current_media.hotspots)}
                            </div>
                        </div>
                        <div className="popup_description">
                            <div className="popup_nav">
                                <span className="prev" onClick={this.prevMedia.bind(this)}>
                                    <svg xmlns="http://www.w3.org/2000/svg" width="11.745" height="22.075" viewBox="0 0 11.745 22.075">
                                      <path id="Path_1" data-name="Path 1" d="M1154.684,309.5,1144,320.184l10.684,10.684" transform="translate(-1143.293 -309.146)" fill="none" stroke="#707070" stroke-width="1"/>
                                    </svg>
                                </span>
                                <span className="next" onClick={this.nextMedia.bind(this)}>
                                    <svg xmlns="http://www.w3.org/2000/svg" width="11.745" height="22.075" viewBox="0 0 11.745 22.075">
                                      <path id="Path_2" data-name="Path 2" d="M10.684,0,0,10.684,10.684,21.368" transform="translate(11.038 21.722) rotate(180)" fill="none" stroke="#707070" stroke-width="1"/>
                                    </svg>
                                </span>
                            </div>
                            <div className={typeof this.state.current_media.hotspots !== "undefined" && this.state.current_media.hotspots.length > 0 ? "tagged_product_list not_empty" : "tagged_product_list"}>
                                <Slider dot={false} infinite={false} speed={750} slidesPerRow={3} slidesToScroll={1}
                                        rows={2} arrows={true} draggable={false} responsive={[
                                        {
                                            breakpoint: 768,
                                            settings: {
                                                slidesToShow: 1.25,
                                                slidesPerRow: 2,
                                                rows: 1
                                            }
                                        }
                                    ]}  >
                                    {this.generateTaggedProductsHtml(this.state.current_media.hotspots)}
                                </Slider>
                            </div>
                            {(() => {
                                if (this.isBackend()) {
                                    return <ButtonGroup>
                                        <div className="media_control_wrapper">
                                            <Button primary onClick={() => {
                                                this.state.product_picker_open = true;
                                                this.setState(this.state);
                                            }}>Tag Products</Button>
                                            {(()=>{
                                                if (this.state.slider_settings.toggleDisplay) {
                                                    return <Button secondary onClick={() => {
                                                        this.toggleMediaDisplay(this.state.current_media.id)
                                                    }}>{this.state.current_media.show ? 'Hide this Media' : 'Show this Media'}
                                                    </Button>
                                                }
                                            })()}

                                        </div>
                                    </ButtonGroup>
                                }
                            })()}
                            <span className="popup_caption"><a href={'https://www.instagram.com/'+this.state.current_media.username} className="username">@{this.state.current_media.username} </a> {this.state.current_media.caption}</span>
                            <a className="view-on-instagram" target="_blank" href={this.state.current_media.permalink}>
                                <span className="view-on-instagram-text">View on Instagram</span>
                            </a>
                            <div className="popup_social_share">
                                <a className="popup_social_facebook" href={'https://facebook.com/sharer/sharer.php?u=' + encodeURIComponent(this.state.current_media.permalink)} target="_blank">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="13.662" height="13.662" viewBox="0 0 13.662 13.662">
                                      <path id="Icon_awesome-facebook-square" data-name="Icon awesome-facebook-square" d="M12.2,2.25H1.464A1.464,1.464,0,0,0,0,3.714V14.449a1.464,1.464,0,0,0,1.464,1.464H5.649V11.267H3.728V9.081H5.649V7.415A2.668,2.668,0,0,1,8.506,4.473,11.64,11.64,0,0,1,10.2,4.62V6.48H9.246A1.093,1.093,0,0,0,8.013,7.662v1.42h2.1l-.335,2.186H8.013v4.645H12.2a1.464,1.464,0,0,0,1.464-1.464V3.714A1.464,1.464,0,0,0,12.2,2.25Z" transform="translate(0 -2.25)" fill="#afafaf"/>
                                    </svg>
                                </a>
                                <a className="popup_social_twitter"  href={'https://twitter.com/intent/tweet/?text=' + encodeURIComponent('#'+this.state.current_media.username) + '&url=' + encodeURIComponent(this.state.current_media.permalink)}  target="_blank">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="15.614" height="12.682" viewBox="0 0 15.614 12.682">
                                      <path id="Icon_awesome-twitter" data-name="Icon awesome-twitter" d="M14.009,6.541c.01.139.01.277.01.416a9.606,9.606,0,0,1-3.065,6.866,8.635,8.635,0,0,1-6.04,2.239A9.043,9.043,0,0,1,0,14.626a6.62,6.62,0,0,0,.773.04A6.409,6.409,0,0,0,4.746,13.3a3.206,3.206,0,0,1-2.992-2.219,4.035,4.035,0,0,0,.6.05,3.385,3.385,0,0,0,.842-.109A3.2,3.2,0,0,1,.634,7.879v-.04a3.223,3.223,0,0,0,1.446.406,3.2,3.2,0,0,1-.991-4.28,9.1,9.1,0,0,0,6.6,3.349,3.613,3.613,0,0,1-.079-.733,3.2,3.2,0,0,1,5.538-2.19,6.3,6.3,0,0,0,2.031-.773,3.191,3.191,0,0,1-1.407,1.764,6.415,6.415,0,0,0,1.843-.5,6.879,6.879,0,0,1-1.6,1.655Z" transform="translate(0 -3.381)" fill="#afafaf"/>
                                    </svg>
                                </a>
                                <a className="popup_social_mail"  href={'mailto:?subject=&body=' + encodeURIComponent('#' + this.state.current_media.username + "\n" + this.state.current_media.permalink)} >
                                    <svg id="Icon_ionic-ios-mail" data-name="Icon ionic-ios-mail" xmlns="http://www.w3.org/2000/svg" width="16.472" height="11.404" viewBox="0 0 16.472 11.404">
                                      <path id="Path_13" data-name="Path 13" d="M19.712,10.338l-4.261,4.34a.077.077,0,0,0,0,.111l2.982,3.176a.514.514,0,0,1,0,.729.516.516,0,0,1-.729,0l-2.97-3.164a.081.081,0,0,0-.115,0l-.725.736a3.188,3.188,0,0,1-2.273.958,3.252,3.252,0,0,1-2.32-.986l-.7-.709a.081.081,0,0,0-.115,0l-2.97,3.164a.516.516,0,0,1-.729,0,.514.514,0,0,1,0-.729l2.982-3.176a.084.084,0,0,0,0-.111L3.51,10.338a.078.078,0,0,0-.135.055v8.683a1.271,1.271,0,0,0,1.267,1.267H18.58a1.271,1.271,0,0,0,1.267-1.267V10.394A.079.079,0,0,0,19.712,10.338Z" transform="translate(-3.375 -8.94)" fill="#afafaf"/>
                                      <path id="Path_14" data-name="Path 14" d="M11.983,15.125a2.153,2.153,0,0,0,1.548-.649l6.213-6.323a1.244,1.244,0,0,0-.784-.277H5.01a1.236,1.236,0,0,0-.784.277l6.213,6.323A2.153,2.153,0,0,0,11.983,15.125Z" transform="translate(-3.747 -7.875)" fill="#afafaf"/>
                                    </svg>
                                </a>
                                <a className="popup_social_mail"  href="javascript:void(0)">
                                    <CopyToClipboard text={this.state.current_media.permalink}>
                                      <svg xmlns="http://www.w3.org/2000/svg" width="11.367" height="11.732" viewBox="0 0 11.367 11.732">
                                          <g id="Icon_feather-link" data-name="Icon feather-link" transform="translate(0.5 0.688)">
                                            <path id="Path_9" data-name="Path 9" d="M15,8.7a2.591,2.591,0,0,0,3.907.28L20.461,7.43A2.59,2.59,0,1,0,16.8,3.766l-.891.886" transform="translate(-10.853 -3.008)" fill="none" stroke="#afafaf" stroke-linecap="round" stroke-linejoin="round" stroke-width="1"/>
                                            <path id="Path_10" data-name="Path 10" d="M9.212,14.531a2.591,2.591,0,0,0-3.907-.28L3.752,15.806a2.59,2.59,0,1,0,3.663,3.663l.886-.886" transform="translate(-2.993 -9.871)" fill="none" stroke="#afafaf" stroke-linecap="round" stroke-linejoin="round" stroke-width="1"/>
                                          </g>
                                        </svg>
                                    </CopyToClipboard>
                                </a>
                            </div>
                        </div>
                        <span className="close" onClick={() => {
                                                this.state.open = false;
                                                this.setState(this.state);
                                            }}>
                                    <svg xmlns="http://www.w3.org/2000/svg" width="22.207" height="22.207" viewBox="0 0 22.207 22.207">
                                          <g id="Group_1" data-name="Group 1" transform="translate(0.354 0.354)">
                                            <line id="Line_1" data-name="Line 1" x2="21.5" y2="21.5" transform="translate(0 0)" fill="none" stroke="#707070" stroke-width="1"/>
                                            <line id="Line_2" data-name="Line 2" x1="21.5" y2="21.5" transform="translate(0 0)" fill="none" stroke="#707070" stroke-width="1"/>
                                          </g>
                                    </svg>
                        </span>
                    </div>
                    {(() => {
                        return this.resourcePicker();
                    })()}
                </Modal>
                <Modal
                    large={false}
                    instant={true}
                    open={this.state.loader}
                    loading={true}>
                </Modal>

            </AppProvider>
        );
    }

    retrieveSettings() {
        var self = this;
        if (self.retrievedFlag) {
            return;
        }
        var url = getUrl('instagram-feed-settings'),
            shop = '',
            params = [];
        if (this.isBackend()) {
            shop = appConfig.shop_origin;
        } else {
            shop = Shopify.shop;
        }

        params.push('shop=' + shop);

        if (this.isProductSlider()) {
            var matches = document.location.pathname.match(/products\/(.*)/i);
            var productHandle = matches ? matches[1] : '';
            params.push('product_handle=' + productHandle);
        }

        if (this.isBackend()) {
            params.push('backend=1')
        }

        url = url + '?' + params.join('&');

        fetch(url, {
            cache: 'no-cache'
        }).then(
            (response) => response.json()
        ).then((data) => {
            if (typeof data == 'object') {
                self.state.medias = data.medias;
                self.state.slider_settings = data.slider_settings;
                if (this.isBackend() || this.isProductSlider()) {
                    self.state.slider_settings.width = 100;
                }
                if (this.isProductSlider()) {
                    self.state.slider_settings.rows = 1;
                    self.state.slider_settings.slidesPerRow = 4;
                }
                self.setState(self.state);
                if (data.slider_settings.buttonColor) {
                    document.documentElement.style.setProperty('--buy-button-color', data.slider_settings.buttonColor);
                }
            }
            self.retrievedFlag = true;
        }).catch((error) => {
            console.error('Error:', error);
            self.retrievedFlag = true;
        });
    }

    saveHotspot(data) {
        var self = this;
        return $.ajax(
            '/instagram/hotspot/save',
            {
                method: 'POST',
                dataType: 'json',
                data: JSON.stringify({
                    params: data
                }),
                contentType: 'application/json',
                beforeSend: () => {
                    self.state.loader = true;
                    self.setState(self.state);
                }
            }
        ).done((res) => {
            if (typeof res.result == 'object') {
                var hotspots = res.result;
                self.state.current_media.hotspots = hotspots;
                self.setState(self.state);
            } else {
                console.log(res);
                alert(res.result);
            }
        }).always(() => {
            self.state.loader = false;
            self.setState(self.state);
        })
    }

    toggleMediaDisplay(mediaId) {
        var self = this;
        return $.ajax(
            '/instagram/media/toggle_display',
            {
                method: 'POST',
                dataType: 'json',
                data: JSON.stringify({
                    params: {media_id: mediaId}
                }),
                contentType: 'application/json',
                beforeSend: () => {
                    self.state.loader = true;
                    self.setState(self.state);
                }
            }
        ).done((res) => {
            if (typeof res.result == 'boolean') {
                self.state.current_media.show = res.result;
                self.setState(self.state);
            } else {
                console.log(res);
                alert(res.result);
            }
        }).always(() => {
            self.state.loader = false;
            self.setState(self.state);
        })
    }

    handleProductSelection = (resources) => {
        var self = this;
        this.saveHotspot({
            product: resources.selection[0],
            media: self.state.current_media,
            top_perc: 50,
            left_perc: 50
        }).fail((res) => {
            console.log(res);
            alert(res);
        }).always(() => {
            self.state.product_picker_open = false;
            self.setState(self.state);
        })
    };
}

export {InstagramSlider};

if (typeof document != "undefined") {
    import('jquery').then((module) => {
        $ = module.default;
        $(document).ready(() => {
            const wrapper = document.getElementById("af_insta_slider");
            wrapper ? ReactDOM.render(<InstagramSlider/>, wrapper) : false;
        });
        $(document).ready(() => {
            const wrapper = document.getElementById("af_insta_product_slider");
            if (wrapper) {
                ReactDOM.render(<InstagramSlider isProductSlider={true}/>, wrapper);
            }
        })
    });
}