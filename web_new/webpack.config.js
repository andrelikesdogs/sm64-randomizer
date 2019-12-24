const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const FaviconsWebpackPlugin = require("favicons-webpack-plugin");

const webpack = require("webpack");

const isProduction = process.env.NODE_ENV === "production";
const publicPath = process.env.PUBLIC_PATH

module.exports = {
  entry: "./src/index.js",
  output: {
    path: path.resolve(__dirname, "..", "docs"),
    publicPath: "",
    filename: isProduction ? "bundle.[hash].js" : "bundle.js"
  },
  target: "web",
  resolve: {
    symlinks: false,
    alias: {
      "react-dom": "@hot-loader/react-dom",
      assets: path.resolve(__dirname, "assets"),
      scss: path.resolve(__dirname, "src", "scss"),
    },
    modules: ["node_modules", "src", "assets"]
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /(node_modules)/,
        use: "babel-loader"
      },
      {
        test: /\.s?css$/,
        use: [
          "style-loader",
          {
            loader: "css-loader",
            options: {
              modules: {
                localIdentName: "[name]__[local]--[hash:base64:5]"
              }
            }
          },
          "sass-loader"
        ]
      },
      {
        test: /\.woff2?(\?v=\d+\.\d+\.\d+)?$/,
        use: {
          loader: "file-loader",
          options: {
            name: "[name].[ext]",
            outputPath: "fonts/"
          }
        },
        include: [path.resolve(__dirname, "assets", "fonts")]
      },
      {
        test: /\.(png|svg|jpg|gif)$/,
        use: ["file-loader"],
        exclude: [path.resolve(__dirname, "assets", "icons")]
      },
      {
        test: /.*\/icons\/.*\.svg$/,
        use: {
          loader: "svg-url-loader",
          options: {
            stripdeclarations: true
          }
        }
      }
    ]
  },
  plugins: [
    new HtmlWebpackPlugin({
      filename: "index.html",
      template: path.resolve(__dirname, "src", "index.html")
    }),
    new FaviconsWebpackPlugin({
      logo: path.resolve(__dirname, "assets", "img", "logo.png"),
      publicPath: "./",
      prefix: "assets"
    }),
    new webpack.EnvironmentPlugin({
      NODE_ENV: "development",
    })
  ]
};
