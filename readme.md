<a href="https://compani.ai" target="_blank"><img alt="Compani AI" src="./modcandy/site/static/basic_logo.png" width="full"></a>

# ModCandy

ModCandy is a powerful open-source tool designed by [Compani AI](https://compani.ai) to help businesses moderate user-generated content across various platforms, including social media, gaming, e-commerce, and more. It provides both a basic Version and a profiled Version for analyzing the toxicity of messages and interactions in real-time. The API uses advanced algorithms to score messages based on their level of toxicity, providing a seamless way to flag and moderate harmful content automatically.

To learn more about the API, check out the [documentation 📕](https://docs.compani.ai/).


# Quick Start

```bash
git clone https://github.com/companiai/modcandy.git
cd modcandy
pip install -r requirements.txt
./manage.py runserver
```

And don't forget to create `.env` file and [Perspective API Key](https://perspectiveapi.com/)

```bash
PERSPECTIVE_API_KEY=12345678
```

## Roadmap
- [✔] Perspective Integration with fix-weight algorithm
- [✔] Custom blacklist and whitelist
- [ ] Docker version  
- [ ] Dashboard for reports and stats  
- [ ] Easy pipeline for training variable weights with custom dataset
- [ ] Agentic AI Moderation System for contextual analysis
- [ ] Custom Machine Learning model by Compani AI
- [ ] Fine-tune the model for better performance
- [ ] Create demos for various usecases
- [ ] Voice Moderation


## Contributing

We love contributions! Feel free to open issues for bugs or feature requests.

## Citation

If you use Modcandy in your research or project, please cite:

```bibtex
@software{modcandy,
  author = {Sachin, Singh and Dmitrijs Vitjazevs},
  title = {Compani AI, AI powered content moderation},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/companiai/modcandy}
}
```

<div align="center">
  Made with ❤️ in Bali
</div>
